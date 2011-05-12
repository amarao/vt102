# -*- coding: utf-8 -*-
"""
    customscreen
    ~~~~~~~~~~~~

    What if you need a custom screen, which for example maintains a list
    of "dirty" (i. e. changed) lines. You got it :)
"""



class DiffScreen(Screen):
    """A screen subclass, which maintains a set of dirty lines in its
    :attr:`dirty` attribute. The end user is responsible for emptying
    a set, when a diff is applied.

    .. attribute:: dirty

       A set of line numbers, which should be re-drawn.

       >>> screen = DiffScreen(80, 24)
       >>> screen.dirty.clear()
       >>> screen.draw(u"!")
       >>> screen.dirty
       set([0])
    """
    def __init__(self, *args):
        self.dirty = set()
        super(DiffScreen, self).__init__(*args)

    def reset(self):
        self.dirty.update(xrange(self.lines))
        super(DiffScreen, self).reset()

    def resize(self, *args, **kwargs):
        self.dirty.update(xrange(self.lines))
        super(DiffScreen, self).resize(*args, **kwargs)

    def draw(self, *args):
        self.dirty.add(self.y)
        super(DiffScreen, self).draw(*args)

    def index(self):
        if self.y == self.margins.bottom:
            self.dirty.update(xrange(self.lines))

        super(DiffScreen, self).index()

    def reverse_index(self):
        if self.y == self.margins.top:
            self.dirty.update(xrange(self.lines))

        super(DiffScreen, self).reverse_index()

    def insert_lines(self, *args):
        self.dirty.update(xrange(self.y, self.lines))
        super(DiffScreen, self).insert_lines(*args)

    def delete_lines(self, *args):
        self.dirty.update(xrange(self.y, self.lines))
        super(DiffScreen, self).delete_lines(*args)

    def insert_characters(self, *args):
        self.dirty.add(self.y)
        super(DiffScreen, self).insert_characters(*args)

    def delete_characters(self, *args):
        self.dirty.add(self.y)
        super(DiffScreen, self).delete_characters(*args)

    def erase_characters(self, *args):
        self.dirty.add(self.y)
        super(DiffScreen, self).erase_characters(*args)

    def erase_in_line(self, *args):
        self.dirty.add(self.y)
        super(DiffScreen, self).erase_in_line(*args)

    def erase_in_display(self, type_of=0):
        self.dirty.update((
            xrange(self.y + 1, self.lines),
            xrange(0, self.y),
            xrange(0, self.lines)
        )[type_of])
        super(DiffScreen, self).erase_in_display(type_of)

    def alignment_display(self):
        self.dirty.update(xrange(self.y, self.lines))
        super(DiffScreen, self).alignment_display()
