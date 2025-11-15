# a list consisting 100 names
names = ["Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace", "Hannah", "Ian", "Jack",
         "Kathy", "Liam", "Mia", "Noah", "Olivia", "Paul", "Quinn", "Rachel", "Sam", "Tina",
         "Uma", "Vince", "Wendy", "Xander", "Yara", "Zane", "Aaron", "Bella", "Cody", "Diana",
         "Ethan", "Fiona", "Gavin", "Hailey", "Isaac", "Jenna", "Kevin", "Luna", "Mason", "Nina",
         "Owen", "Piper", "Quentin", "Riley", "Sophia", "Tyler", "Ursula", "Victor", "Willow",
         "Ximena", "Yusuf", "Zara", "Adam", "Bianca", "Caleb", "Delilah", "Elijah", "Faith",
         "Graham", "Hazel", "Isaiah", "Jocelyn", "Kaden", "Leah", "Miles", "Nora", "Oscar",
         "Penelope", "Quincy", "Ruby", "Sebastian", "Trinity", "Ulric", "Valeria", "Wyatt", "Xavier", "Yvonne", "Zachary", "sujan"]


for name in names:
    # print(name)
    if name =='Caleb':
        print("found Caleb")
        break
else:
    print("Caleb not found")
    
    
    
    
    
# # Install packages if not already installed
# # !pip install matplotlib

# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# from IPython.display import clear_output
# import time
# from pathlib import Path

# # Ensure plots directory next to this script
# OUT_DIR = Path(__file__).resolve().parent / "plots"
# OUT_DIR.mkdir(parents=True, exist_ok=True)

# # simple counter to number saved plots
# _plot_counter = 0

# # ---------- Helper Functions ----------
# def draw_boxes(items, title="Collection", highlight=None):
#     """
#     Draws boxes for each item in a collection.
#     highlight: index to highlight (optional)
#     """
#     clear_output(wait=True)
#     fig, ax = plt.subplots(figsize=(len(items)*1.2,2))
#     ax.set_xlim(0, len(items)+1)
#     ax.set_ylim(0, 2)
#     ax.axis('off')
    
#     for i, item in enumerate(items):
#         color = 'lightgreen' if i == highlight else 'skyblue'
#         rect = patches.Rectangle((i+0.5, 0.5), 1, 1, edgecolor='black', facecolor=color)
#         ax.add_patch(rect)
#         ax.text(i+1, 1, str(item), ha='center', va='center', fontsize=12)
        
#     ax.set_title(title, fontsize=14)

#     # Save figure to plots directory instead of showing (headless-friendly)
#     global _plot_counter
#     _plot_counter += 1
#     safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title).strip()
#     filename = OUT_DIR / f"{_plot_counter:02d}_{safe_title.replace(' ', '_')}.png"
#     fig.savefig(filename, dpi=150, bbox_inches='tight')
#     plt.close(fig)
#     print(f"Saved plot: {filename}")
#     time.sleep(1)

# # ---------- 1️⃣ List Playground ----------
# print("=== List Playground ===")
# fruits = ['apple', 'banana', 'cherry']
# draw_boxes(fruits, "Initial List")

# fruits[1] = 'blueberry'
# draw_boxes(fruits, "Changed 2nd Item", highlight=1)

# fruits.append('orange')
# draw_boxes(fruits, "Added 'orange'", highlight=len(fruits)-1)

# fruits.remove('apple')
# draw_boxes(fruits, "Removed 'apple'")

# # ---------- 2️⃣ Tuple Playground ----------
# print("=== Tuple Playground ===")
# colors = ('red', 'green', 'blue')
# draw_boxes(colors, "Tuple (Immutable)")

# # ---------- 3️⃣ Set Playground ----------
# print("=== Set Playground ===")
# unique_fruits = list({'apple', 'banana', 'cherry', 'apple'})  # remove duplicates
# draw_boxes(unique_fruits, "Set (Duplicates Removed)")

# unique_fruits.append('orange')
# draw_boxes(unique_fruits, "Added 'orange'", highlight=len(unique_fruits)-1)

# unique_fruits.remove('banana')
# draw_boxes(unique_fruits, "Removed 'banana'")

# # ---------- 4️⃣ Dictionary Playground ----------
# print("=== Dictionary Playground ===")
# person = {'name': 'Alice', 'age': 25, 'city': 'New York'}
# dict_items = [f"{k}:\n{v}" for k,v in person.items()]
# draw_boxes(dict_items, "Dictionary Initial")

# person['age'] = 26
# dict_items = [f"{k}:\n{v}" for k,v in person.items()]
# draw_boxes(dict_items, "Updated Age")

# person['job'] = 'Engineer'
# dict_items = [f"{k}:\n{v}" for k,v in person.items()]
# draw_boxes(dict_items, "Added Job", highlight=len(dict_items)-1)

# del person['city']
# dict_items = [f"{k}:\n{v}" for k,v in person.items()]
# draw_boxes(dict_items, "Removed City")
