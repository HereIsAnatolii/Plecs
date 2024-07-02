class PLECS_TAGS():
  def __init__(self,tag_name):
    self.tag = {'Type':"",
     'Name': f'"{tag_name}"',
     'Show': 'off',
     'Position':[0,0],
     'Direction':'right',
     'Flipped':'off',
     'LabelPosition':'south',
     'Parameter_1':{'Variable':'"Tag"\n','Value':f'"{tag_name}"\n','Show':'off\n'},
     'Parameter_2':{'Variable':'"Visibility"\n','Value':'"1"\n','Show':'off\n'}}
  def set_goto(self):
    self.tag_type = "Goto"
    self.tag['Type'] = self.tag_type
  def set_from(self):
    self.tag_type = "From"
    self.tag['Type'] = self.tag_type
  def set_position(self,x,y):
    self.tag['Position'] = [x,y]
  def set_name(self,name):
    self.tag['Parameter_1']['Value'] = f'"{name}"'
  def make_global(self):
    self.tag['Parameter_2']['Value'] = '"1"'
  def make_local(self):
    self.tag['Parameter_2']['Value'] = '"2"'
  def print_tag(self):
    line = []
    line.append("\tComponent {\n")
    for key,value in self.tag.items():
      if key.split('_')[0] == 'Parameter':
        line.append("\tParameter {\n")
        for inner_key,inner_value in self.tag[key].items():
          line.append(f'\t\t\t{inner_key:<10} {inner_value}')
          line.append('\t\t}\n')
      else:
        line.append(f'\t\t{key:<20} {value}\n')
        line.append("\t}\n")
      return line

# Create tags from 0 to N
N = 3
tags = [[],[]]
name = 'Sc.'
for i in range(N):
  tags[0].append(PLECS_TAGS(f"{name}{i+1}"))
  tags[0][i].set_goto()
  tags[0][i].make_local()
#  tags[0][i].make_global()
    
  tags[1].append(PLECS_TAGS(f"{name}{i+1}"))
  tags[1][i].set_from()
  tags[1][i].make_local()
#  tags[1][i].make_global()
    
  tags[0][i].set_position(100,i*50+50)
  tags[1][i].set_position(250,i*50+50)
    
with open('tags.plecs', 'r') as file:
  lines = file.readlines()

line = ['']
for i in range(N):
  line += (tags[0][i].print_tag())
  line += (tags[1][i].print_tag())
new_lines = lines[:-2]+line + ['  }\n'] + ['}']

with open('tags.plecs', 'w') as file:
  for line in new_lines:
    file.write(line)
