// Pandoc PDF engine Typst template (English resume)
// Usage: pandoc out.md -o out.pdf --pdf-engine=typst --template cv/templates/resume.typ
$if(title)$#set document(title: "$title$")$endif$
#set page(margin: (x: 20mm, y: 18mm), numbering: "1")
#set text(size: 10.5pt, lang: "en")
#set par(justify: false, leading: 0.65em)
#show heading.where(level: 1): set text(size: 20pt)
#show heading.where(level: 2): it => [
  #set text(size: 13pt)
  #block(above: 1.2em, below: 0.4em)[#smallcaps(it.body)]
  #line(length: 100%, stroke: 0.5pt + gray)
]
#show heading.where(level: 3): set text(size: 11pt)

$body$
