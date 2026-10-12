"""Crafting snapshots, recipe-holder lookups and registry lookup providers."""
import re

def closing(s,start):
 depth=1;i=start
 while i<len(s):
  if s[i]=='(':depth+=1
  elif s[i]==')':
   depth-=1
   if depth==0:return i
  i+=1
 raise ValueError('Unclosed invocation')

def migrate(root):
 count=0
 for f in (root/'src/main/java').rglob('*.java'):
  s=f.read_text();before=s
  recipe_file='/library/recipe/' in str(f) or '/tables/recipe/' in str(f)
  if recipe_file:
   s=s.replace('import net.minecraft.core.RegistryAccess;', 'import net.minecraft.core.HolderLookup;')
   s=re.sub(r'\bRegistryAccess\b','HolderLookup.Provider',s)
   if 'import net.minecraft.world.inventory.CraftingContainer;' in s:
    s=s.replace('import net.minecraft.world.inventory.CraftingContainer;', 'import net.minecraft.world.item.crafting.CraftingInput;')
    s=re.sub(r'\bCraftingContainer\b','CraftingInput',s)
    # Only parameters declared as CraftingInput; do not change unrelated inventories.
    for name in set(re.findall(r'CraftingInput\s+(\w+)',s)):
     for old,new in [('getContainerSize','size'),('getWidth','width'),('getHeight','height')]:
      s=re.sub(r'\b'+name+r'\.'+old+r'\(\)',name+'.'+new+'()',s)
  if f.name=='ContentTool.java':
   s=s.replace('Recipe<CraftingContainer>','Recipe<net.minecraft.world.item.crafting.CraftingInput>')
  if f.name in ('JEIPlugin.java','RecipeHelper.java','VanillaFilteredRecipe.java','GenerateMeltingRecipesCommand.java'):
   s=s.replace('C extends Container', 'C extends net.minecraft.world.item.crafting.RecipeInput')
  if f.name=='CraftingStationBlockEntity.java':
   s=re.sub(r'(\.matches|\.assemble)\((this\.)?craftingInventory,', lambda m:m[1]+'('+(m[2] or '')+'craftingInventory.asRecipeInput(),',s)
   s=s.replace('RecipeType.CRAFTING, this.craftingInventory,','RecipeType.CRAFTING, this.craftingInventory.asRecipeInput(),')
   s=s.replace('recipe.getRemainingItems(craftingInventory)', 'craftingInventory.recipeRemainders(recipe)')
  if f.name in ('AutosmeltModule.java','SmeltingModule.java'):
   name='INVENTORY' if f.name=='AutosmeltModule.java' else 'CONTAINER'
   # Preserve mutable inventory/cache ownership, provide vanilla's immutable recipe view at the boundary.
   s=re.sub(r'(?<=[(,])\s*'+name+r'(?=,)', ' new net.minecraft.world.item.crafting.SingleRecipeInput('+name+'.getStack())',s)
  # Original callers consume recipes, while RecipeManager now returns RecipeHolder.
  for method in ('getRecipeFor','byKey','getAllRecipesFor'):
   edits=[]
   for m in re.finditer(r'\.'+method+r'\(',s):
    end=closing(s,m.end())+1
    suffix='.map(net.minecraft.world.item.crafting.RecipeHolder::value)' if method!='getAllRecipesFor' else '.stream().map(net.minecraft.world.item.crafting.RecipeHolder::value).toList()'
    edits.append((end,suffix))
   for end,suffix in reversed(edits):s=s[:end]+suffix+s[end:]
  edits=[]
  for m in re.finditer(r'\.byType\(',s):
   end=closing(s,m.end())+1
   tail=re.match(r'\s*\.values\(\)',s[end:])
   if tail:
    edits.append((m.start(),end+tail.end(),'.getAllRecipesFor('+s[m.end():end-1]+').stream().map(net.minecraft.world.item.crafting.RecipeHolder::value).toList()'))
   elif s[end:].startswith('.isEmpty()'):
    edits.append((m.start(),end,'.getAllRecipesFor('+s[m.end():end-1]+')'))
  for a,b,new in reversed(edits):s=s[:a]+new+s[b:]
  if s!=before:f.write_text(s);count+=1
 # Add explicit snapshot/remainder mapping to the real crafting inventory wrapper.
 f=root/'src/main/java/slimeknights/tconstruct/tables/block/entity/inventory/CraftingContainerWrapper.java'
 s=f.read_text();pos=s.rfind('}')
 s=s[:pos]+'''
  /** Snapshot with vanilla trimming semantics for recipe matching and assembly. */
  public net.minecraft.world.item.crafting.CraftingInput asRecipeInput() {
    return net.minecraft.world.item.crafting.CraftingInput.of(width, height, getItems());
  }

  /** Restore trimmed recipe remainder slots to their original positions in the machine. */
  public net.minecraft.core.NonNullList<ItemStack> recipeRemainders(net.minecraft.world.item.crafting.CraftingRecipe recipe) {
    var positioned = net.minecraft.world.item.crafting.CraftingInput.ofPositioned(width, height, getItems());
    var input = positioned.input();
    var remaining = recipe.getRemainingItems(input);
    var result = net.minecraft.core.NonNullList.withSize(getContainerSize(), ItemStack.EMPTY);
    for (int y=0; y<input.height(); y++) {
      for (int x=0; x<input.width(); x++) {
        result.set((y+positioned.top())*width+x+positioned.left(), remaining.get(y*input.width()+x));
      }
    }
    return result;
  }
'''+s[pos:]
 f.write_text(s)
 return count
