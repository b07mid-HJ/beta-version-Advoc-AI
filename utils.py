from docx import Document

def fill_cont(template_path,output_path,contract_data):
    # Load the template
    doc = Document(template_path)

    # Fill in the contract data
    for key, value in contract_data.items():
        for paragraph in doc.paragraphs:
            if key in paragraph.text:
                paragraph.text = paragraph.text.replace(key, value)

    # Save the filled contract
    doc.save(output_path)