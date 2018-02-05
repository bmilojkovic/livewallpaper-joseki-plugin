#!/usr/bin/env bash
sudo cp joseki.xml /usr/lib/livewallpaper/plugins/joseki/
sudo cp joseki.py /usr/lib/livewallpaper/plugins/joseki/
sudo cp go_stone.py /usr/lib/livewallpaper/plugins/joseki/
sudo cp go_algorithm.py /usr/lib/livewallpaper/plugins/joseki/
sudo cp joseki.plugin /usr/lib/livewallpaper/plugins/joseki/
sudo cp net.launchpad.livewallpaper.plugins.joseki.gschema.xml /usr/share/glib-2.0/schemas/
sudo cp kaya.png /usr/share/livewallpaper/plugins/joseki/
sudo cp desk.png /usr/share/livewallpaper/plugins/joseki/
sudo cp livewallpaper-joseki.svg /usr/share/icons/hicolor/scalable/apps/
sudo cp example.sgf /usr/share/livewallpaper/plugins/joseki/
sudo cp kjd.sgf /usr/share/livewallpaper/plugins/joseki/
sudo /usr/bin/glib-compile-schemas /usr/share/glib-2.0/schemas/
pkill livewallpaper
livewallpaper-config
