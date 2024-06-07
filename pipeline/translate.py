import pathlib
import opencc

# t2s.json is the configuration file for Traditional to Simplified conversion
converter = opencc.OpenCC("t2s")

# Specify the folder path containing the files to translate
input_folder_path = pathlib.Path("../content/zh_TW/post")

# Specify the folder path to save the translated files
output_folder_path = pathlib.Path("../content/zh_CN/post")

# Create the output folder if it doesn't exist
output_folder_path.mkdir(parents=True, exist_ok=True)

# Loop through each file in the input folder
for input_file_path in input_folder_path.glob("*.md"):
    # Read the contents of the input file
    with open(input_file_path, "r", encoding="utf-8") as input_file:
        content = input_file.read()

    # Convert Traditional Chinese to Simplified Chinese
    converted_content = converter.convert(content)

    # Append zh-cn to all post links
    converted_content = converted_content.replace('href="/post/', 'href="/zh-cn/post/')

    # Create the output file path by replacing the input folder path with the output folder path
    output_file_path = output_folder_path / input_file_path.relative_to(
        input_folder_path
    )

    # Write the converted content to the output file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(converted_content)

print("Translation complete!")
