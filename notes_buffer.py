import sublime, sublime_plugin
import os, fnmatch, re

TAB_SIZE = 2
COL_WIDTH = 30

def settings():
    return sublime.load_settings('Notes.sublime-settings')

class NotesBufferCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.new_file()
        view.set_scratch(True)
        view.set_name("✎ Notes Index")
        view.set_syntax_file('Packages/PlainNotes/Notes Index.hidden-tmLanguage')
        view.settings().set('color_scheme', 'Packages/PlainNotes/Color Schemes/Notes-Index.hidden-tmTheme')
        self.window.focus_view(view)
        view.run_command('notes_buffer_refresh')

class NotesBufferRefreshCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view
        v.set_read_only(False)
        v.erase(edit, sublime.Region(0, self.view.size()))
        root = os.path.normpath(os.path.expanduser(settings().get("root")))
        lines = self.list_files(root)

        v.settings().set('notes_buffer_files', lines)

        v.insert(edit, 0, "\n".join([f[0] for f in lines]))
        v.set_read_only(True)

    def list_files(self, path):
        lines = []
        for root, dirs, files in os.walk(path, topdown=False):
            level = root.replace(path, '').count(os.sep) - 1
            indent = ' ' * TAB_SIZE * (level)
            relpath = os.path.relpath(root, path)
            if  not (relpath == "." or relpath == ".brain" or relpath == ".archive"):
                line_str = '{0}▣ {1}'.format(indent, os.path.relpath(root, path))
                lines.append( (line_str, root) )
            if  not (relpath == ".brain" or relpath == ".archive"):
                subindent = ' ' * TAB_SIZE * (level + 1)
                for f in files:
                    line_str = '{0}≡ {1}'.format(subindent, re.sub('\.note$', '', f))
                    line_path = os.path.normpath(os.path.join(root, f))
                    lines.append( (line_str, line_path)  )
        return lines


class NotesBufferOpenCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view
        for sel in v.sel():
            file_index = v.rowcol(sel.a)[0]
            files = v.settings().get('notes_buffer_files')
            file_path = files[file_index][1]

            def open_and_activate():
              view = sublime.active_window().open_file(file_path, sublime.ENCODED_POSITION)
              f_id = file_id(file_path)
              if db.get(f_id) and db[f_id]["color_scheme"]:
                view.settings().set("color_scheme", db[f_id]["color_scheme"])
                view.settings().set("is_note", True)

            sublime.set_timeout(open_and_activate, 0)
