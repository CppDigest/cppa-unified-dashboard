# HTML to Markdown Conversion Report

## Source data

The conversion process targeted HTML and HTM files from the WG21 paper collection. A total of 6,112 HTML/HTM files were processed for conversion to Markdown format.

| File Type | Count | Percentage |
| --------- | ----- | ---------- |
| `.html`   | 5,714 | 93.5%      |
| `.htm`    | 398   | 6.5%       |
| **TOTAL** | 6,112 | 100.0%     |

## HTML Conversion process

HTML conversion used a three-step process with Pandoc (via pypandoc) as the primary conversion tool.

Pandoc is a bit slow and highly customizable, preserving almost all formatting elements, leading to verbose markdown. Best for academic or documentation conversion where precision matters. [https://github.com/sanand0/tools-in-data-science-public/blob/main/convert-html-to-markdown.md#pandoc]

### Conversion workflow

1. The HTML content is pre-processed to ensure the main tag contains all HTML content, preparing it for Pandoc conversion.

2. Pandoc processes the pre-processed HTML files and converts them to Markdown format using automated batch processing.

3. Any remaining HTML tags are post-processed and converted to Markdown syntax, and HTML tables are converted to Markdown table format.

### Storage Size Comparison

- **Source folder size:** 1.48 GB
- **Converted folder size:** 1.07 GB
- **Size reduction:** 420.57 MB (27.82% smaller)

### Line Count Comparison

- **Total lines in HTML/HTM files:** 20,052,291
- **Total lines in converted MD files:** 9,284,546
- **Line difference:** -10,767,745 (-53.70%)

### Pandoc conversion

Pandoc converted all 6,112 HTML/HTM files (100.0% success rate). The process used automated batch processing to convert HTML files to Markdown format.

- Advantages

  - 100% conversion success rate
  - Automated processing handles large volumes efficiently
  - Preserves document structure in most cases
  - Converts HTML elements to the right Markdown syntax
  - Handles tables, lists, and formatting elements
  - Reliable and consistent output

- Disadvantages

  - Some code blocks get converted inline and code gets converted wrong (like `&lt;`) (e.g. 2023/08/p2863r1.md - L429)
  - Some HTML tags (like `<del>` and `<ins>`) don't get converted to markdown (e.g. 2016/11/p0003r5.md - L210-220)
  - Too many blank lines show up in some converted files (e.g. 1995/N0760.md - L2-4, 2014/11/n4332.md - L1623-1625)
  - Some formatting gets messed up in complex HTML structures (e.g. 2020/11/p0447r11.md - L251)

## Quality assessment

A random sample of 20 converted HTML files was analyzed to assess conversion quality. The assessment shows:

- Most files converted with acceptable quality
- Document structure generally preserved accurately
- HTML elements converted to appropriate Markdown syntax in most cases
- Tables, lists, and formatting elements handled correctly
- Some code block formatting issues in a small number of files
- Some HTML tags not fully converted to Markdown in certain cases
- Excessive blank lines appear in some converted files
- Complex HTML structures may result in formatting inconsistencies

**Note:** HTML conversion using Pandoc achieves 100% success rate with all 6,112 files successfully converted. The conversion process reduces file size by approximately 28% and line count by approximately 54% due to Markdown's more compact syntax compared to HTML markup. Pandoc's three-step process (pre-processing, conversion, and post-processing) ensures comprehensive conversion of HTML elements to Markdown format. While most files convert with acceptable quality, some complex HTML structures and certain HTML tags may require manual review for optimal results.
