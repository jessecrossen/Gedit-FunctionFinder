from gi.repository import GObject, Gtk, Gdk, Gedit

import re
import subprocess
import difflib

class FunctionFinder(GObject.Object, Gedit.ViewActivatable):
  __gtype_name__ = "FunctionFinder"
  view = GObject.property(type=Gedit.View)
  
  def __init__(self):
    GObject.Object.__init__(self)
    self._handler_id = None
    # whether we're actively searching for a function
    self.searching = False
    # the current search text
    self.search = ''
    # an index of definitions to search through
    self.index = dict()
    # compile a regex of searchable characters
    self.is_searchable_key = re.compile(r'^\w$')
    # set up the key binding
    self.accel = Gtk.accelerator_parse('<Primary>r')
  
  # hook and unhook from view events
  def do_activate(self):
    # retain a reference to the document
    self.doc = self.view.get_buffer()
    # bind events
    self._handler_id = self.view.connect('event', self.on_event)
  def do_deactivate(self):
    # unbind events
    if (self._handler_id is not None):
      self.view.disconnect(self._handler_id)
      self._handler_id = None
    # exit search mode
    self.stop_searching()
      
  def on_event(self, view, event):
    if (event.type == Gdk.EventType.KEY_PRESS):
      keyval = Gdk.keyval_to_lower(event.keyval)
      mask = Gtk.accelerator_get_default_mod_mask() & event.state
      # start searching when the accelerator is used
      if ((keyval, mask) == self.accel):
        self.start_searching()
        return(True)
      # handle other keystrokes only in search mode
      elif (self.searching):
        key = Gdk.keyval_name(keyval)
        if (key == 'BackSpace'):
          self.search = self.search[:-1]
          self.update_search()
          return('True')
        elif (self.is_searchable_key.match(key)):
          self.search += key
          self.update_search()
          return('True')
        # don't exit if the user hits shift
        elif (key.startswith('Shift')):
          return('True')
        # exit on Enter without inserting it and 
        #  select the function name
        elif (key == 'Return'):
          found = self.update_search()
          if (found is not None):
            self.doc.select_range(found[0], found[1])
          self.stop_searching()
          return(True)
        else:
          self.stop_searching()
          return(False)
    # stop searching if the user clicks
    if (event.type == Gdk.EventType.BUTTON_PRESS):
      self.stop_searching()
    return(False)
  
  # start search mode
  def start_searching(self):
    # make sure we can index the document
    if (self.index_document()):
      self.searching = True
      self.search = ''
    
  # search for the current text
  def update_search(self):
    matches = difflib.get_close_matches(
      self.search, self.index.keys(), 1, 0.1)
    if (len(matches) < 1): return
    match = matches[0]
    line = self.index[match]
    pos = self.doc.get_start_iter()
    # try to show one line above the function definition
    pos.set_line(max(0, line - 2))
    self.view.scroll_to_iter(pos, 0.0, True, 0.0, 0.0)
    # highlight the matched name
    tag = self.get_tag()
    pos.set_line(max(0, line - 1))
    end_pos = pos.copy()
    end_pos.forward_to_line_end()
    found = pos.forward_search(
      match, Gtk.TextSearchFlags.CASE_INSENSITIVE, end_pos)
    # remove any existing tag
    self.remove_tag()
    # add the new tag
    if (found is not None):
      self.doc.apply_tag(tag, found[0], found[1])
    # return the location of the match
    return(found)
  
  # end search mode
  def stop_searching(self):
    if (self.searching):
      self.searching = False
      self.search = ''
      self.remove_tag()
    
  # make an index of definitions in the file to search
  def index_document(self):
    # clear the index
    self.index = dict()
    # get the file's location if any
    path = self.doc.get_location().get_path()
    if (path is None):
      return(False)
    # run the file through ctags
    lines = subprocess.check_output(
      ('ctags', '-f', '-', '--fields=Kn', path))
    lines = lines.split('\n')
    for line in lines:
      # parse tag lines
      parts = line.split('\t')
      if (len(parts) != 5): continue
      (name, f, p, kind, line) = parts
      # skip variables
      if (kind == 'variable'): continue
      # user lower case to match without case sensitivity
      name = name.lower()
      # strip off the 'line:' part to just get the line number
      line = int(line[5:])
      # index the definition
      self.index[name] = line
    return(True)
    
  # get a tag to apply to the search match
  def get_tag(self):
    tag = self.doc.get_tag_table().lookup('found-function')
    if (tag is None):
      background = '#FFFF00'
      foreground = self.get_view_color('text_color')
      (background, foreground) = self.get_scheme_colors(
        'search-match', (background, foreground))
      tag = self.doc.create_tag('found-function', 
                                background=background, 
                                foreground=foreground)
    return(tag)
    
  # remove all instances of the tag
  def remove_tag(self):
    if (self.doc.get_tag_table().lookup('found-function') is not None):
      self.doc.remove_tag_by_name('found-function',
        self.doc.get_start_iter(), self.doc.get_end_iter())
  
  # get the default color for the given style property of the view
  def get_view_color(self, color_name):
    return(self.view.get_style().lookup_color(color_name)[1].to_string())
  
  # get the given foreground and background colors from the current 
  #  style scheme, falling back on the given defaults
  def get_scheme_colors(self, style_name, defaults):
    scheme = self.doc.get_style_scheme()
    if (scheme is not None):
      sel_style = scheme.get_style(style_name)
      if (sel_style is not None):
        return(sel_style.get_property('background'), 
               sel_style.get_property('foreground'))
    return(defaults)
    
