from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.widget import Widget
import json
import os

# Colors
BG       = (0.047, 0.047, 0.055, 1)
SURFACE  = (0.094, 0.094, 0.109, 1)
ACCENT   = (0.831, 0.961, 0.416, 1)   # lime green
MUTED    = (0.42, 0.42, 0.48, 1)
TEXT     = (0.94, 0.94, 0.94, 1)
RED      = (1, 0.42, 0.42, 1)

SAVE_FILE = os.path.join(os.path.expanduser("~"), "todo_tasks.json")


def load_tasks():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(SAVE_FILE, "w") as f:
        json.dump(tasks, f)


class RoundedBox(Widget):
    def __init__(self, bg_color=SURFACE, radius=18, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self.radius])


class TaskRow(BoxLayout):
    def __init__(self, task_text, done, on_toggle, on_delete, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None,
                         height=dp(64), spacing=dp(12), padding=[dp(16), dp(10)], **kwargs)
        self.task_text = task_text
        self.done = done
        self.on_toggle = on_toggle
        self.on_delete = on_delete

        with self.canvas.before:
            Color(*(SURFACE))
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._upd, size=self._upd)

        # Checkbox button
        self.check_btn = Button(
            size_hint=(None, None), size=(dp(32), dp(32)),
            background_normal='', background_color=(0, 0, 0, 0),
            text='✓' if done else '', font_size=dp(16),
            color=(0.047, 0.047, 0.055, 1) if done else (0, 0, 0, 0),
        )
        self._draw_check()
        self.check_btn.bind(on_press=lambda _: self.on_toggle())
        self.add_widget(self.check_btn)

        # Task label
        self.lbl = Label(
            text=('[s]' + task_text + '[/s]') if done else task_text,
            markup=True,
            color=(*MUTED[:3], 1) if done else TEXT,
            font_size=dp(15),
            halign='left', valign='middle',
            text_size=(None, None),
        )
        self.lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        self.add_widget(self.lbl)

        # Delete button
        del_btn = Button(
            text='🗑', font_size=dp(18),
            size_hint=(None, None), size=(dp(36), dp(36)),
            background_normal='', background_color=(0, 0, 0, 0),
            color=(*MUTED[:3], 1),
        )
        del_btn.bind(on_press=lambda _: self.on_delete())
        self.add_widget(del_btn)

    def _upd(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _draw_check(self):
        self.check_btn.canvas.before.clear()
        with self.check_btn.canvas.before:
            if self.done:
                Color(*ACCENT)
            else:
                Color(*MUTED)
            RoundedRectangle(pos=self.check_btn.pos,
                             size=self.check_btn.size,
                             radius=[dp(16)])
        self.check_btn.bind(pos=self._recheck, size=self._recheck)

    def _recheck(self, *_):
        self._draw_check()


class StatBox(BoxLayout):
    def __init__(self, label, value, **kwargs):
        super().__init__(orientation='vertical', size_hint=(1, None),
                         height=dp(64), padding=[0, dp(8)], **kwargs)
        with self.canvas.before:
            Color(*SURFACE)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._u, size=self._u)

        self.val_lbl = Label(text=str(value), font_size=dp(24),
                             bold=True, color=ACCENT,
                             size_hint_y=None, height=dp(30))
        self.add_widget(self.val_lbl)
        self.add_widget(Label(text=label, font_size=dp(10),
                              color=MUTED, size_hint_y=None, height=dp(18)))

    def _u(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def set_value(self, v):
        self.val_lbl.text = str(v)


class TodoApp(App):
    def build(self):
        Window.clearcolor = BG
        self.tasks = load_tasks()
        self.filter = 'all'

        root = BoxLayout(orientation='vertical', spacing=0)

        # ── Header ──
        header = BoxLayout(orientation='vertical',
                           size_hint_y=None, height=dp(200),
                           padding=[dp(24), dp(40), dp(24), dp(12)],
                           spacing=dp(10))
        with header.canvas.before:
            Color(*BG)
            Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(i.canvas.before.children[-1], 'pos', v),
                    size=lambda i, v: setattr(i.canvas.before.children[-1], 'size', v))

        header.add_widget(Label(
            text='DEINE AUFGABEN',
            font_size=dp(11), color=MUTED,
            size_hint_y=None, height=dp(18),
            halign='left', text_size=(Window.width, None),
        ))
        header.add_widget(Label(
            text='Was steht heute an?',
            font_size=dp(28), bold=True, color=TEXT,
            size_hint_y=None, height=dp(40),
            halign='left', text_size=(Window.width, None),
        ))

        # Stats row
        stats_row = BoxLayout(orientation='horizontal', spacing=dp(10),
                              size_hint_y=None, height=dp(64))
        self.stat_total = StatBox('Gesamt', len(self.tasks))
        self.stat_open  = StatBox('Offen',  len([t for t in self.tasks if not t['done']]))
        self.stat_done  = StatBox('Erledigt', len([t for t in self.tasks if t['done']]))
        stats_row.add_widget(self.stat_total)
        stats_row.add_widget(self.stat_open)
        stats_row.add_widget(self.stat_done)
        header.add_widget(stats_row)

        root.add_widget(header)

        # ── Filter tabs ──
        tabs = BoxLayout(orientation='horizontal', size_hint_y=None,
                         height=dp(44), padding=[dp(20), dp(4)], spacing=dp(8))
        self.tab_btns = {}
        for key, label in [('all', 'Alle'), ('open', 'Offen'), ('done', 'Erledigt')]:
            btn = Button(text=label, font_size=dp(12),
                         background_normal='', background_color=(0,0,0,0),
                         size_hint_x=None, width=dp(72), height=dp(32))
            btn.bind(on_press=lambda _, k=key: self.set_filter(k))
            self.tab_btns[key] = btn
            tabs.add_widget(btn)
        root.add_widget(tabs)
        self._style_tabs()

        # ── Scroll list ──
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.task_container = BoxLayout(
            orientation='vertical', spacing=dp(10),
            size_hint_y=None, padding=[dp(20), dp(4), dp(20), dp(100)]
        )
        self.task_container.bind(minimum_height=self.task_container.setter('height'))
        self.scroll.add_widget(self.task_container)
        root.add_widget(self.scroll)

        # ── Input bar ──
        input_bar = BoxLayout(orientation='horizontal', size_hint_y=None,
                              height=dp(72), padding=[dp(16), dp(12)], spacing=dp(10))
        with input_bar.canvas.before:
            Color(*BG)
            Rectangle(pos=input_bar.pos, size=input_bar.size)
        input_bar.bind(pos=lambda i, v: setattr(i.canvas.before.children[-1], 'pos', v),
                       size=lambda i, v: setattr(i.canvas.before.children[-1], 'size', v))

        self.text_input = TextInput(
            hint_text='Neue Aufgabe hinzufügen…',
            multiline=False, font_size=dp(15),
            foreground_color=TEXT,
            hint_text_color=MUTED,
            background_color=SURFACE,
            cursor_color=ACCENT,
            padding=[dp(14), dp(12)],
        )
        self.text_input.bind(on_text_validate=self.add_task)
        input_bar.add_widget(self.text_input)

        add_btn = Button(
            text='+', font_size=dp(26), bold=True,
            size_hint=(None, None), size=(dp(48), dp(48)),
            background_normal='', background_color=ACCENT,
            color=(0.047, 0.047, 0.055, 1),
        )
        with add_btn.canvas.before:
            Color(*ACCENT)
            self._add_bg = RoundedRectangle(pos=add_btn.pos,
                                            size=add_btn.size, radius=[dp(12)])
        add_btn.bind(pos=lambda i, v: setattr(self._add_bg, 'pos', v),
                     size=lambda i, v: setattr(self._add_bg, 'size', v),
                     on_press=self.add_task)
        input_bar.add_widget(add_btn)
        root.add_widget(input_bar)

        self.render_tasks()
        return root

    def _style_tabs(self):
        for key, btn in self.tab_btns.items():
            btn.canvas.before.clear()
            with btn.canvas.before:
                if key == self.filter:
                    Color(*ACCENT)
                else:
                    Color(*SURFACE)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(20)])
            btn.color = (0.047, 0.047, 0.055, 1) if key == self.filter else MUTED
            btn.bind(pos=lambda i, v, k=key: self._redraw_tab(k),
                     size=lambda i, v, k=key: self._redraw_tab(k))

    def _redraw_tab(self, key):
        btn = self.tab_btns[key]
        btn.canvas.before.clear()
        with btn.canvas.before:
            if key == self.filter:
                Color(*ACCENT)
            else:
                Color(*SURFACE)
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(20)])

    def set_filter(self, key):
        self.filter = key
        self._style_tabs()
        self.render_tasks()

    def add_task(self, *_):
        text = self.text_input.text.strip()
        if text:
            self.tasks.insert(0, {'text': text, 'done': False})
            save_tasks(self.tasks)
            self.text_input.text = ''
            self.render_tasks()

    def toggle_task(self, idx):
        self.tasks[idx]['done'] = not self.tasks[idx]['done']
        save_tasks(self.tasks)
        self.render_tasks()

    def delete_task(self, idx):
        self.tasks.pop(idx)
        save_tasks(self.tasks)
        self.render_tasks()

    def render_tasks(self):
        self.task_container.clear_widgets()

        total = len(self.tasks)
        done  = len([t for t in self.tasks if t['done']])
        open_ = total - done
        self.stat_total.set_value(total)
        self.stat_open.set_value(open_)
        self.stat_done.set_value(done)

        filtered = [(i, t) for i, t in enumerate(self.tasks)
                    if (self.filter == 'all') or
                       (self.filter == 'open' and not t['done']) or
                       (self.filter == 'done' and t['done'])]

        if not filtered:
            msg = {
                'all':  'Noch keine Aufgaben!\nTippe unten etwas ein ✨',
                'open': 'Alles erledigt! Super 🎉',
                'done': 'Noch nichts abgehakt.',
            }[self.filter]
            self.task_container.add_widget(
                Label(text=msg, color=MUTED, font_size=dp(15),
                      halign='center', size_hint_y=None, height=dp(100))
            )
            return

        for idx, task in filtered:
            row = TaskRow(
                task_text=task['text'],
                done=task['done'],
                on_toggle=lambda i=idx: self.toggle_task(i),
                on_delete=lambda i=idx: self.delete_task(i),
            )
            self.task_container.add_widget(row)


if __name__ == '__main__':
    TodoApp().run()
