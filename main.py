import io
from typing import Dict, List, Tuple
from PIL import Image
from pdf2image import convert_from_bytes
from augmatrix.block_service.service_runner import ServerManager, ServiceRunner
import fitz

class SplitPDFTask(ServiceRunner):
    def __init__(self, logger: object) -> None:
        """
        Initializes the SplitPDFTask object.

        Parameters:
        logger (object): The logger to use for logging messages.
        """
        self.logger = logger
        super().__init__(structure_json_path='./structure.json')

    def split_pdf_to_images(self, pdf: bytes) -> Tuple[List[bytes], List[bytes]]:
        """
        Splits a PDF file into separate pages and converts each page to a separate image.

        Parameters:
        pdf (bytes): A byte string representing the input PDF file.

        Returns:
        Tuple[List[bytes], List[bytes]]: A tuple containing two lists of bytes:
            - A list of byte strings representing the individual images extracted from the PDF.
            - A list of byte strings representing the individual PDFs (each containing a single page).
        """

        # Open the original PDF from bytes
        pil_images = convert_from_bytes(pdf)
        images, split_pdfs = [], []
        
        with fitz.open("pdf", pdf) as doc:
            for i in range(len(doc)):
                # Convert each page to an image
                img_byte_array = io.BytesIO()
                pil_images[i].save(img_byte_array, format="PNG")
                images.append(img_byte_array.getvalue())

                # Create a new PDF for each page
                pdf_byte_array = io.BytesIO()
                new_doc = fitz.open()  # Create a new PDF in memory
                new_doc.insert_pdf(doc, from_page=i, to_page=i)  # Insert the current page
                new_doc.save(pdf_byte_array)  # Save the new one-page PDF to bytes
                split_pdfs.append(pdf_byte_array.getvalue())
                new_doc.close()  # Close the new doc to avoid memory leaks

        return images, split_pdfs

    def run(self, inputs, properties, credentials):
        result_list = []
        for image_byte_data, pdf_byte_data in zip(*self.split_pdf_to_images(inputs.pdf)):
            result_list.append({"image": image_byte_data, "pdf": pdf_byte_data})

        return result_list

if __name__ == "__main__":
    ServerManager(SplitPDFTask(logger=None)).start(
        host="localhost",
        port=8082,
        # private_key="certificates/private.pem",
        # cert_key="certificates/cert.pem"
    )
