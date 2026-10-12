"""Replace obsolete Container-based recipe views with actual 1.21 RecipeInput views."""
import re

def migrate(root):
 changed=0
 names={
  'ISingleStackContainer':('slimeknights.mantle.recipe.container.ISingleStackContainer','slimeknights.tconstruct.library.recipe.input.TinkerSingleItemInput','TinkerSingleItemInput'),
  'IRecipeContainer':('slimeknights.mantle.recipe.container.IRecipeContainer','slimeknights.tconstruct.library.recipe.input.TinkerRecipeInput','TinkerRecipeInput'),
  'IEmptyContainer':('slimeknights.mantle.recipe.container.IEmptyContainer','slimeknights.mantle.recipe.input.NoItemInput','NoItemInput'),
 }
 for f in (root/'src/main/java').rglob('*.java'):
  s=f.read_text();before=s
  for old,(path,new_path,new) in names.items():
   if path in s:
    s=s.replace(path,new_path)
    s=re.sub(r'\b'+old+r'\b',new,s)
  if f.name in ('IPartBuilderContainer.java','IMoldingContainer.java','ITinkerableContainer.java'):
   s=s.replace('default int getContainerSize()', 'default int size()')
  if s!=before:f.write_text(s);changed+=1
 return changed
