from augmatrix.block_service.data_context import encode, decode, decode_to_object
from augmatrix.datasets import variable_def_to_dataclass
import logging
import httpx
import json

logging.basicConfig(level=logging.DEBUG)

def send_request(url, data, method='POST', content_type='application/msgpack'):
    """
    Send data to a server using HTTP/2 and MessagePack as the content type with httpx.
    """
    headers = {'content-type': content_type}
    # Using httpx for HTTP/2 support
    with httpx.Client(http2=True) as client:
        if method.upper() == 'POST':
            print("Sent request")
            response = client.post(url, content=data, headers=headers, timeout=600)
            print("Received response")
        # Add other methods as needed
        else:
            raise ValueError("Unsupported method")
    return response.content

def main():
    # Specify the server's URL
    url = 'http://localhost:8082/'

    with open("testdata/single_pdf.pdf", "rb") as fr, open("structure.json", "r") as fr_struct:
        structure = json.loads(fr_struct.read())
        func_args_dataclass = variable_def_to_dataclass(structure['func_args_schema'], 'FunctionArguments')
        inputs_dataclass = variable_def_to_dataclass(structure['inputs_schema'], 'Inputs')
        outputs_dataclass = variable_def_to_dataclass(structure['outputs_schema'], 'Outputs')

        inputs = inputs_dataclass(pdf=fr.read())
        func_arguments = func_args_dataclass(properties=json.dumps(structure['block_properties']), credentials=json.dumps({}))

        func_args_data = encode(func_arguments)
        inputs_data = encode(inputs)
        data_dict = {'func_args': func_args_data, 'inputs': inputs_data}

        b_data = encode(data_dict)

        # Send data to the server and process the response
        response_data = decode(send_request(url, b_data))

        outputs = [decode_to_object(output, outputs_dataclass) for output in response_data]

        print(outputs)

if __name__ == "__main__":
    main()