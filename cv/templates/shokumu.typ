// Pandoc PDF エンジン用 Typst テンプレート（日本語職務経歴書）
// 使用: pandoc out.md -o out.pdf --pdf-engine=typst --template cv/templates/shokumu.typ
// フォントは環境に合わせて調整可（Windows 11 標準の "Yu Gothic" を既定に、
// 未検出時は Typst が自動フォールバック）。
$if(title)$#set document(title: "$title$")$endif$
#set page(margin: (x: 20mm, y: 18mm), numbering: "1")
#set text(font: ("Yu Gothic", "Meiryo", "MS Gothic"), size: 10pt, lang: "ja")
#set par(justify: false, leading: 0.7em)
#show heading.where(level: 1): set text(size: 18pt)
#show heading.where(level: 2): it => [
  #set text(size: 12pt)
  #block(above: 1.2em, below: 0.5em)[#it.body]
  #line(length: 100%, stroke: 0.5pt + gray)
]
#show heading.where(level: 3): set text(size: 11pt)

$body$
