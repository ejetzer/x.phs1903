-----------------------------------------------------------------------
--         FILE:  xindex-sort-pattern.lua
--  DESCRIPTION:  modified configuration file for xindex.lua
-- REQUIREMENTS:
--       AUTHOR:  Herbert Voß and Marcel Krüger
--      LICENSE:  LPPL1.3
-----------------------------------------------------------------------

itemPageDelimiter = ","     -- Hello, 14
compressPages     = true    -- something like 12--15, instead of 12,13,14,15. the |( ... |) syntax is still valid
fCompress     = true    -- 3f -> page 3, 4 and 3ff -> page 3, 4, 5
minCompress       = 3       -- 14--17 or
rangeSymbol       = "--"
numericPage       = true    -- for non numerical pagenumbers, like "VI-17"
sublabels         = {"", "-\\,", "--\\,", "---\\,"} -- for the (sub(sub(sub-items  first one is for item
pageNoPrefixDel   = ""     -- a delimiter for page numbers like "VI-17"  -- not used !!!
indexOpening      = "\\let\\bigletter\\sphinxstyleindexlettergroup\\let\\spxpagem \\sphinxstyleindexpagemain\\let\\spxentry \\sphinxstyleindexentry\\let\\spxextra \\sphinxstyleindexextra"     -- commands after \begin{theindex}
idxnewletter      = "  \\bigletter"  -- Only valid if -n is not set
