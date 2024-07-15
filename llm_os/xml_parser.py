import xml.etree.ElementTree as ET
from typing import Optional
import re


class ToolParser:
    """Parses XML tool calling markup from LLM output."""

    @staticmethod
    def xml_to_dict(xml_string: str) -> Optional[dict]:
        """Parse XML string to dictionary, including inner text for simple elements."""
        try:
            root = ET.fromstring(xml_string)
            result_dict = {root.tag: {} if root.attrib or list(root) else root.text}
            for child in list(root):
                if child.text:
                    result_dict[root.tag][child.tag] = child.text.strip()  # type: ignore
                else:
                    result_dict[root.tag][child.tag] = child.attrib  # type: ignore
            return result_dict
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return None

    @staticmethod
    def extract_and_parse_xml(raw_string: str) -> list[dict]:
        """Extract XML strings and convert to dictionary with enhanced regex."""
        # Enhanced regex pattern to better capture nested and more complex XML
        xml_pattern = r"<(\w+)[^>]*>(.*?)</\1>"
        xml_strings = re.findall(xml_pattern, raw_string, re.DOTALL)

        # Parse all found XML strings to dictionaries
        parsed_xmls = []
        for xml_match in xml_strings:
            xml_content = f"<{xml_match[0]}>{xml_match[1]}</{xml_match[0]}>"
            parsed_xml = ToolParser.xml_to_dict(xml_content)
            if parsed_xml:
                parsed_xmls.append(parsed_xml)

        return parsed_xmls
