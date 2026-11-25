-- Each preview comes from its essay's first paragraph, including inline formatting.
local function list_posts(div)
  if not div.classes:includes("post-list") then return end
  local posts = {}
  for _, name in ipairs(pandoc.system.list_directory("posts")) do
    if name:match("%.qmd$") then
      local file = assert(io.open("posts/" .. name))
      local source = file:read("*a")
      file:close()
      local post = pandoc.read(source, "markdown+yaml_metadata_block")
      local opening = post.blocks[1]
      assert(opening and opening.t == "Para", name .. " must start with a paragraph")
      table.insert(posts, {
        name = name, title = assert(post.meta.title), opening = opening,
        date = post.meta.date and pandoc.utils.stringify(post.meta.date) or ""
      })
    end
  end
  if #posts == 0 then
    return pandoc.Para({pandoc.Emph(div.attributes["empty-message"] or "Following soon!")})
  end
  table.sort(posts, function(a, b)
    if a.date == b.date then return a.name < b.name end
    return a.date > b.date
  end)
  local items = div.content
  local limit = tonumber(div.attributes.limit) or #posts
  for i = 1, math.min(limit, #posts) do
    local post = posts[i]
    local url = "posts/" .. post.name:gsub("%.qmd$", ".html")
    local blocks = pandoc.List({
      pandoc.Header(2, {pandoc.Link(post.title, url)}, pandoc.Attr("", {"essay-title"}))
    })
    if post.date ~= "" then
      blocks:insert(pandoc.Para({pandoc.Span(post.date, pandoc.Attr("", {"date"}))}))
    end
    blocks:insert(post.opening)
    blocks:insert(pandoc.Para({pandoc.Link("Continue reading", url .. "#paragraph-two", "", pandoc.Attr("", {"read"}))}))
    items:insert(pandoc.Div(blocks, pandoc.Attr("", {"post-preview"})))
  end
  return items
end

function Pandoc(doc)
  if doc.meta.story then
    local count = 0
    for i, block in ipairs(doc.blocks) do
      if block.t == "Para" then
        count = count + 1
        if count == 2 then
          doc.blocks[i] = pandoc.Div({block}, pandoc.Attr("paragraph-two"))
          return doc
        end
      end
    end
    error("An essay needs a second paragraph for Continue reading.")
  end
  return doc:walk({Div = list_posts})
end
