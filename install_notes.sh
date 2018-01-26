sudo cp joseki.xml /usr/lib/livewallpaper/plugins/joseki/
sudo cp joseki.py /usr/lib/livewallpaper/plugins/joseki/
sudo cp joseki.plugin /usr/lib/livewallpaper/plugins/joseki/
sudo cp net.launchpad.livewallpaper.plugins.joseki.gschema.xml /usr/share/glib-2.0/schemas/
sudo cp kaya.png /usr/share/livewallpaper/plugins/joseki/
sudo /usr/bin/glib-compile-schemas /usr/share/glib-2.0/schemas/
pkill livewallpaper
livewallpaper-config

#make /usr/share/livewallpaper/plugins/joseki and insert sgf files