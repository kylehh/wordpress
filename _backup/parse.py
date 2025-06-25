import xml.etree.ElementTree as ET
import os
import re
from datetime import datetime

def parse_wordpress_xml(xml_file):
    """
    Parses a WordPress XML export file and generates markdown files for each post.

    Args:
        xml_file (str): The path to the WordPress XML file.
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return

    # Create a directory to store the markdown files
    output_dir = "markdown_posts"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Namespace dictionary for finding elements
    ns = {
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'wp': 'http://wordpress.org/export/1.2/',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }

    for item in root.findall('.//item'):
        post_type = item.find('wp:post_type', ns).text
        if post_type == 'post':
            title = item.find('title').text
            # It's better to use post_date_gmt for a consistent timezone
            pub_date_gmt_str = item.find('wp:post_date_gmt', ns).text
            
            # Handle potential '0000-00-00 00:00:00' dates
            if pub_date_gmt_str and pub_date_gmt_str != '0000-00-00 00:00:00':
                try:
                    pub_date = datetime.strptime(pub_date_gmt_str, '%Y-%m-%d %H:%M:%S')
                    date_str = pub_date.strftime('%y-%m-%d')
                except ValueError:
                    print(f"Could not parse date for post: '{title}'. Using '00-00-00'.")
                    date_str = "00-00-00"
            else:
                date_str = "00-00-00"

            # Sanitize the title for use in a filename
            sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)
            sanitized_title = sanitized_title.replace(" ", "-").lower()
            filename = f"{date_str}-{sanitized_title}.md"
            filepath = os.path.join(output_dir, filename)

            content_encoded = item.find('content:encoded', ns).text
            
            # Start markdown content with post title and content
            markdown_content = f"# {title}\n\n"
            if content_encoded:
                markdown_content += content_encoded + "\n\n"
            else:
                 markdown_content += "*(No content)*\n\n"


            markdown_content += "## Comments\n\n"
            
            # Find and process comments for the current post
            comments = item.findall('wp:comment', ns)
            if comments:
                for comment in comments:
                    author = comment.find('wp:comment_author', ns).text
                    comment_content = comment.find('wp:comment_content', ns).text
                    markdown_content += f"**{author}**:\n"
                    if comment_content:
                        markdown_content += f"> {comment_content}\n\n"
                    else:
                        markdown_content += "> *(No comment content)*\n\n"
            else:
                markdown_content += "*(No comments for this post)*\n"

            # Write the markdown content to the file
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print(f"Generated: {filename}")
            except IOError as e:
                print(f"Error writing to file {filename}: {e}")


if __name__ == '__main__':
    # Make sure to place the XML file in the same directory as the script
    # or provide the correct path.
    xml_filename = 'site.wordpress.2025-06-25.000.xml' 
    if os.path.exists(xml_filename):
        parse_wordpress_xml(xml_filename)
        print("\nParsing complete. Markdown files are in the 'markdown_posts' directory.")
    else:
        print(f"Error: The file '{xml_filename}' was not found in the current directory.")


