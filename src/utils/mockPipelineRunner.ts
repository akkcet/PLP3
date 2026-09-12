/**
 * Mock XML model parser and pipeline runner utilities for client-side simulator
 */

export interface ParsedModelFile {
  file_name: string;
  file_location: string;
  section_title: string;
  extension: string;
}

export interface ParsedModelMetadata {
  section_name: string;
  base_location: string;
  files: ParsedModelFile[];
}

export function parse_model_xml(xmlString: string): ParsedModelMetadata {
  const parser = new DOMParser();
  const xmlDoc = parser.parseFromString(xmlString, "text/xml");

  const generics = xmlDoc.getElementsByTagName("generic");
  const files: ParsedModelFile[] = [];
  let section_name = "";
  let base_location = "";

  for (let i = 0; i < generics.length; i++) {
    const generic = generics[i];
    const titleElem = generic.getElementsByTagName("XML_title")[0];
    const elnElem = generic.getElementsByTagName("ELN_value")[0];

    const title = titleElem?.textContent?.trim() || "Untitled Section";
    if (!section_name && title) {
      section_name = title;
    }

    if (elnElem?.textContent) {
      const rawPath = elnElem.textContent.trim();
      const normPath = rawPath.replace(/\\/g, "/");
      const parts = normPath.split("/");
      const fileName = parts[parts.length - 1];

      if (!base_location) {
        const usersIdx = normPath.indexOf("users");
        const lastSlash = normPath.lastIndexOf("/");
        if (usersIdx !== -1 && lastSlash !== -1) {
          base_location = normPath.substring(usersIdx, lastSlash);
        }
      }

      const dotIdx = fileName.lastIndexOf(".");
      const extension = dotIdx !== -1 ? fileName.substring(dotIdx).toLowerCase() : "";

      files.push({
        file_name: fileName,
        file_location: rawPath,
        section_title: title,
        extension,
      });
    }
  }

  return {
    section_name: section_name || "Spectroscopy Data Model",
    base_location: base_location || "users/arun.khuntia/experiments",
    files,
  };
}
