import os

import pygame as pg

from math import floor

from useful import load_image, colors


class HeroSelector(pg.Surface):
    size = width, height = 320, 280  #TODO: finalise these

    def __init__(self):
        super(HeroSelector, self).__init__(self.size)

        self.choice = ''

        self._load_images()

        self._base = self._make_base()
        self._draw_base()

    def _make_base(self):
        base = pg.Surface(self.get_size(), 0, self)

        base.fill(colors.yellow)
        base.fill(colors.bgblue, (1, 1, self.width - 2, self.height - 2))

        if not self.choice:
            for i, (_, img) in enumerate(sorted(self.hero_icon_s.items())):
                w, h = img.get_size()
                cx, cy = w / 2, h / 2
                base.blit(img, ((2 * (i % 3) + 1) * self.width / 6 - cx,
                                (2 * (i / 3) + 1) * self.height / 6 - cy))
        else:
            img = self.hero_icon[self.choice]
            w, h = img.get_size()
            base.blit(img, (self.width / 2 - w / 2,
                            self.height / 2 - h / 2))

        return base

    def _draw_base(self):
        self.blit(self._base, (0, 0))

    def _draw_tile(self, pos, flavour="hover"):
        x, y = pos % 3, pos / 3

        if flavour.lower() == "hover":
            tile = self._tile_hover
        else:
            tile = self._tile_selected

        self.blit(tile, (x * self.width / 3,
                         y * self.height / 3))

    def handle_mouse_input(self, mouseobj, offset=(0, 0)):
        self._draw_base()

        mx, my = mouseobj.get_pos()
        presses = mouseobj.get_pressed()

        mx -= offset[0]
        my -= offset[1]

        if not self.get_rect().collidepoint(mx, my):
            return

        ix = mx / (self.width / 3)
        iy = my / (self.height / 3)

        pos = iy * 3 + ix

        if not self.choice:
            if presses[0]:
                self.choice = self.hero_names[pos]

                self._base = self._make_base()
                self._draw_base()
            else:
                self._draw_tile(pos)
        elif presses[2]:
            self.choice = ''

            self._base = self._make_base()
            self._draw_base()

    @classmethod
    def _load_images(cls):
        if "heroes" in cls.__dict__:
            #we've done this before for another instance
            return

        cls.hero_icon = {}
        cls.hero_icon_s = {}
        cls.hero_names = []
        path = r"resource\class_icons"
        for img in os.listdir(path):
            hero_icon = load_image(os.path.join(path, img),
                                   colorkey=colors.white)
            hero_icon_s = pg.transform.smoothscale(hero_icon, (64, 64))

            hero_name = img.split('.')[0]

            cls.hero_icon[hero_name] = hero_icon
            cls.hero_icon_s[hero_name] = hero_icon_s

            cls.hero_names.append(hero_name)

        cls.hero_names = tuple(cls.hero_names)

        #tiles
        base_tile = pg.Surface((cls.width / 3, cls.height / 3), pg.SRCALPHA)

        cls._tile_hover = base_tile.copy()
        cls._tile_hover.fill((0, 255, 255, 64))

        cls._tile_selected = base_tile.copy()
        cls._tile_selected.fill((255, 0, 255, 64))
