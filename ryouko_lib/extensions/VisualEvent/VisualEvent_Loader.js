/**
 * @summary     VisualEvent_Loader
 * @description Loader for VisualEvent - injects the required CSS and Javascript into a page
 * @file        VisualEvent_Loader.js
 * @author      Allan Jardine (www.sprymedia.co.uk)
 * @license     GPL v2
 * @contact     www.sprymedia.co.uk/contact
 *
 * @copyright Copyright 2007-2011 Allan Jardine.
 *
 * This source file is free software, under the GPL v2 license:
 *   http://www.gnu.org/licenses/gpl-2.0.html
 */(function(a,b){typeof VisualEvent_Loader=="undefined"&&(a.VisualEvent_Loader=function(){if(!this instanceof VisualEvent_Loader){alert("VisualEvent loader warning: Must be initialised with the 'new' keyword.");return}this.s={loadingComplete:!1},this.dom={loading:b.createElement("div")},this._construct()},VisualEvent_Loader.prototype={_construct:function(){var a=this,c,d;if(this.s.loadingComplete===!0)return 0;c=this.dom.loading,c.setAttribute("id","EventLoading"),c.appendChild(b.createTextNode("Loading Visual Event...")),d=c.style,d.position="fixed",d.bottom="0",d.left="0",d.color="white",d.padding="5px 10px",d.fontSize="11px",d.fontFamily='"Lucida Grande", Verdana, Arial, Helvetica, sans-serif',d.zIndex="55999",d.backgroundColor="#93a8cf",b.body.insertBefore(c,b.body.childNodes[0]),VisualEvent_Loader.jQueryPreLoaded=typeof jQuery=="undefined"?!1:!0;if(typeof VisualEvent=="object"){this._pollReady();return}setTimeout(function(){a._pollReady()},1e3),this._loadFile("http://127.0.0.1:8000/VisualEvent/css/VisualEvent.css","css"),typeof jQuery=="undefined"?this._loadFile("http://127.0.0.1:8000/VisualEvent/js/VisualEvent-jQuery.js","js"):this._loadFile("http://127.0.0.1:8000/VisualEvent/js/VisualEvent.js","js")},_loadFile:function(a,c){var d,e;c=="css"?(d=b.createElement("link"),d.type="text/css",d.rel="stylesheet",d.href=a,d.media="screen",b.getElementsByTagName("head")[0].appendChild(d)):c=="image"?(e=new Image(1,1),e.src=a):(d=b.createElement("script"),d.setAttribute("language","JavaScript"),d.setAttribute("src",a),d.setAttribute("charset","utf8"),b.body.appendChild(d))},_pollReady:function(){var a=this,b;typeof VisualEvent=="function"&&typeof VisualEventSyntaxHighlighter=="object"?this._complete():setTimeout(function(){a._pollReady()},100)},_complete:function(){var a=this;this.s.loadingComplete=!0,c=new VisualEvent,b.body.removeChild(this.dom.loading)}},VisualEvent_Loader.jQueryPreLoaded=!1);var c;typeof VisualEvent!="undefined"?VisualEvent.instance!==null?VisualEvent.close():c=new VisualEvent:c=new VisualEvent_Loader})(window,document);
