

def read_txt(file_path='cookie.txt'):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error reading file: {str(e)}")

    return ''
