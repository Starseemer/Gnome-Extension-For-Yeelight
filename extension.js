const St = imports.gi.St;
const Gio = imports.gi.Gio;
const GLib = imports.gi.GLib;
const ByteArray = imports.byteArray;

const ExtensionUtils = imports.misc.extensionUtils;
const Me = ExtensionUtils.getCurrentExtension();
const Main = imports.ui.main;
const PanelMenu = imports.ui.panelMenu;
const PopupMenu = imports.ui.popupMenu;
const Lang = imports.lang;


const Yeelight_Indicator = new Lang.Class({
        Name: 'Yeelight.indicator',
        Extends: PanelMenu.Button   ,
        _init: function(){
            this.parent(0.0);
            this.add_child(new St.Icon({
                            icon_name: 'display-brightness-symbolic',
                            style_class: 'system-status-icon',
                        }));

            confPath = Me.dir.get_path()+"/config.json";
            log(confPath);
            const [, confs, etag] = Gio.File.new_for_path(confPath).load_contents(null);
            conf = JSON.parse(confs);
            log(conf);
            scenes = conf.Scenes;
            sceneToggles = [];

            for(sceneIndex in scenes){
                log(scenes[sceneIndex].name);
                const sceneToggle = new PopupMenu.PopupSwitchMenuItem(scenes[sceneIndex].name + " Mode",false);
                sceneToggles.push(sceneToggle);
            }

            
            for(var i = 0; i < sceneToggles.length; i++){
                sceneToggles[i].connect('toggled', Lang.bind(this, function(object, value){
                    currentMode = object.label.text.substring(0,object.label.text.length-5)
                    log(currentMode);
                    if(value == true){
                        let output = GLib.spawn_command_line_async('python ' + Me.dir.get_path() + '/main.py -' + currentMode);
                        for(var j = 0; j < sceneToggles.length; j++){
                            if(sceneToggles[j].label.text.substring(0,object.label.text.length-5) != currentMode){
                                sceneToggles[j].setToggleState(false);
                            }
                        }
                    }
                }));
                
            }

            for(var i = 0; i < sceneToggles.length; i++){
                this.menu.addMenuItem(sceneToggles[i]);
            }

            const sep = new PopupMenu.PopupSeparatorMenuItem("PopupSeparatorMenuItem");
            sep.style_class = "PopupSeparatorMenuItem";
			this.menu.addMenuItem(sep);

            bulbs = conf.Bulbs;
			bulbToggles = []

			for(bulbIndex in bulbs){
                log(bulbs[bulbIndex].name);
                const bulbToggle = new PopupMenu.PopupSwitchMenuItem(bulbs[bulbIndex].name + " Toggle",false);
                bulbToggles.push(bulbToggle);
            }


			for(var i = 0; i < bulbToggles.length; i++){
                bulbToggles[i].connect('toggled', Lang.bind(this, function(object, value){
                    currentBulb = object.label.text.substring(0,object.label.text.length-7);
                    let output = GLib.spawn_command_line_async('python ' + Me.dir.get_path() + '/main.py -c --' + currentBulb);
                }));
            }

			for(var i = 0; i < bulbToggles.length; i++){
                this.menu.addMenuItem(bulbToggles[i]);
            }


        },
});

    
function enable() {
        log(`enabling ${Me.metadata.name}`);

        let _indicator =  new Yeelight_Indicator();
        Main.panel._addToPanelBox('Yeelight', _indicator, 1, Main.panel._rightBox);
    }
    

function disable() {
        log(`disabling ${Me.metadata.name}`);

        _indicator.destroy();
        _indicator = null;
}



function init() {
    log(`initializing ${Me.metadata.name}`);
    
}
