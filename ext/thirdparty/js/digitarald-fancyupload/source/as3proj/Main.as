/**
 * Swiff.Uploader
 *
 * Credits: A lot of good parts are inspired by the awesome www.swfupload.org
 *
 * @licence		MIT Licence
 *
 * @author		Harald Kirschner <http://digitarald.de>
 * @author		Anders Rasmussen <aras@dr.dk>
 * @author		Valerio Proietti, <http://mad4milk.net>
 * @copyright	Authors
 */

package
{
	import flash.display.Sprite;
	import flash.display.StageAlign;
	import flash.display.StageScaleMode;
	import flash.display.MovieClip;
	
	import flash.display.Loader;
	
	import flash.events.*;
	import flash.utils.*;
	
	import flash.system.Security;

	import flash.net.FileReference;
	import flash.net.FileReferenceList;
	import flash.net.FileFilter;
	
	import flash.net.URLRequest;

	import flash.external.ExternalInterface;
	
	import flash.text.AntiAliasType;
	import flash.text.GridFitType;
	import flash.text.StaticText;
	import flash.text.StyleSheet;
	import flash.text.TextDisplayMode;
	import flash.text.TextField;
	import flash.text.TextFieldType;
	import flash.text.TextFieldAutoSize;
	import flash.text.TextFormat;

	import Escaper;
	
	import File;
	
	public class Main extends Sprite
	{

		public var options:Object = {
			typeFilter: null,
			typeFilterDescription: null,
			multiple: null,
			queued: null,
			verbose: null,
			width: 128,
			height: 32,
			passStatus: null,
			
			url: null,
			method: null,
			data: null,
			mergeData: null,
			fieldName: null,
			progressGraphSize: 10,
			
			fileSizeMin: 1,
			fileSizeMax: null,// Official 100 MB limit for FileReference
			allowDuplicates: false,
			timeLimit: null,
			
			policyFile: null,
			buttonImage: null
		};
		
		public var fileList:Array = new Array();
		public var uploading:uint = 0;
		
		public var size:uint = 0;
		public var bytesLoaded:uint = 0;
		public var rate:uint = 0;
		
		private var dialog:*= null;
		
		private var buttonLoader:Loader;
		private var buttonCursorSprite:Sprite;
		
		private var buttonState:uint = 0;
		
		const BUTTON_STATE_OVER = 1;
		const BUTTON_STATE_DOWN = 2;
		const BUTTON_STATE_DISABLED = 4;
	
		public function Main():void
		{
			if (stage) init();
			else addEventListener(Event.ADDED_TO_STAGE, init);
		}
		
		private function init(e:Event = null):void
		{
			removeEventListener(Event.ADDED_TO_STAGE, init);
			
			if (!flash.net.FileReference || !flash.external.ExternalInterface || !flash.external.ExternalInterface.available) {
				return;
			}
			
			// allow uploading to any domain
			Security.allowDomain("*");
			
			// ExternalInterface callback adding copied
			ExternalInterface.addCallback('initialize', xInitialize);
			ExternalInterface.addCallback('setOptions', xSetOptions);
			
			ExternalInterface.addCallback('start', xStart);
			ExternalInterface.addCallback('stop', xStop);
			ExternalInterface.addCallback('remove', xRemove);
			
			ExternalInterface.addCallback('setEnabled', xSetEnabled);
			
			ExternalInterface.addCallback('fileSetOptions', xFileSetOptions);
			ExternalInterface.addCallback('fileStart', xFileStart);
			ExternalInterface.addCallback('fileStop', xFileStop);
			ExternalInterface.addCallback('fileRemove', xFileRemove);
			ExternalInterface.addCallback('fileRequeue', xFileRequeue);
			
			fireEvent('load');
		}
		
		public function fireEvent(functionName:String, args:* = null):void
		{
			verboseLog('Main::fireEvent "' + functionName + '"', args);
			
			if (args !== null) {
				if (args is Array) args = Escaper.escapeArray(args);
				else args = [Escaper.escape(args)];
			}
			
			ExternalInterface.call(root.loaderInfo.parameters.fireCallback, functionName, args || []);
		}
		
		private function empty(fake:* = null):void
		{}
		
		// External Interface - JS to Flash - calls
		
		private function xInitialize(options_override:Object = null):void
		{
			xSetOptions(options_override);
			
			// Make the stage clickable and transparent.
			stage.align = StageAlign.TOP_LEFT;
			stage.scaleMode = StageScaleMode.NO_SCALE;
			
			stage.addEventListener(MouseEvent.CLICK, stageClick);
			stage.addEventListener(MouseEvent.MOUSE_DOWN, stageMouse);
			stage.addEventListener(MouseEvent.MOUSE_UP, stageMouse);
			stage.addEventListener(MouseEvent.MOUSE_OVER, stageMouse);
			stage.addEventListener(MouseEvent.MOUSE_OUT, stageMouse);
			stage.addEventListener(Event.MOUSE_LEAVE, stageLeave);
			stage.addEventListener(Event.RESIZE, stageResize);
			
			
			buttonLoader = new Loader();
			buttonLoader.contentLoaderInfo.addEventListener(IOErrorEvent.IO_ERROR, empty);
			buttonLoader.contentLoaderInfo.addEventListener(HTTPStatusEvent.HTTP_STATUS, empty);
			
			stage.addChild(buttonLoader);
			
			
			buttonCursorSprite = new Sprite();
			buttonCursorSprite.graphics.beginFill(0xFFFFFF, 0);
			buttonCursorSprite.graphics.drawRect(0, 0, 1, 1);
			buttonCursorSprite.graphics.endFill();
			buttonCursorSprite.buttonMode = true;
			buttonCursorSprite.useHandCursor = true;
			buttonCursorSprite.x = 0;
			buttonCursorSprite.y = 0;
			buttonCursorSprite.addEventListener(MouseEvent.CLICK, empty);
			
			stage.addChild(buttonCursorSprite);
			
			initButton();
			
			verboseLog('initialized');
		}
		
		private function xSetOptions(options_override:Object = null):void
		{
			if (options_override != null) {
				for (var prop:String in options) {
					if (options_override.hasOwnProperty(prop)) {
						switch (prop) {
							case 'policyFile':
								if (options_override[prop] is String) Security.loadPolicyFile(options_override[prop]);
								break;
						}
						options[prop] = options_override[prop];
					}
				}
			}
		}
		
		private function xFileSetOptions(id:uint, options_init:Object = null):Boolean
		{
			var ref:File = getFileById(id);
			if (!ref) return false;
			
			ref.setOptions(options_init);
			return true;
		}
		
		private function xFileStart(id:uint):Boolean
		{
			var ref:File = getFileById(id);
			if (!ref) return false;
			
			return ref.start();
		}
		
		private function xFileStop(id:uint):Boolean
		{
			var ref:File = getFileById(id);
			if (!ref) return false;
			
			return ref.stop();
		}
		
		private function xFileRemove(id:uint):Boolean
		{
			var ref:File = getFileById(id);
			if (!ref) return false;
			
			return ref.remove();
		}
		
		public function queueUpdate():Object
		{
			return {
				uploading: uploading,
				size: size,
				bytesLoaded: bytesLoaded,
				percentLoaded: (size > 0) ? Math.ceil(bytesLoaded / size * 100) : 0,
				rate: rate
			};
		}
		
		private function xFileRequeue(id:uint):Boolean
		{
			var ref:File = getFileById(id);
			if (!ref) return false;
									
			return ref.requeue();
		}
		
		private function xStart():void
		{
			if (uploading) return;
			checkQueue();
			if (uploading) fireEvent('start');
		}
		
		private function xSetEnabled(status:* = null):void
		{
			if (status == null) status = !(buttonState & BUTTON_STATE_DISABLED);
			
			if (status) buttonState = buttonState &~ BUTTON_STATE_DISABLED;
			else buttonState = buttonState | BUTTON_STATE_DISABLED;
			
			buttonCursorSprite.useHandCursor = status;
			
			updateButton();
		}
		
		private function xStop():void
		{
			for (var i:uint = fileList.length - 1; i > 0; i--) {
				if (fileList[i].status != File.STATUS_RUNNING) continue;
				fileList[i].stop();
			}
		}
		
		private function xRemove():void
		{
			while (fileList.length) {
				fileList[0].remove();
			}
		}
		
		public function checkQueue(eventful:Boolean = false):void
		{
			var queued:uint = (options.queued) ? ((options.queued > 1) ? options.queued : 1) : 0;
			
			if (uploading && queued && uploading >= queued) return;
			
			var length:uint = fileList.length;
			
			for (var i:uint = 0; i < length; i++) {
				if (fileList[i].status != File.STATUS_QUEUED) continue;
				fileList[i].start();
				if (queued && uploading >= queued) break;
			}
			
			if (!uploading && eventful) fireEvent('complete', [queueUpdate()]);
		}
		
		private function stageClick(e:MouseEvent):void
		{
			if (buttonState & BUTTON_STATE_DISABLED) {
				fireEvent('disabledBrowse');
				return;
			}
			
			browse();
		}
		
		private function stageLeave(e:Event):void
		{
			buttonState = buttonState &~ BUTTON_STATE_DOWN;
			buttonState = buttonState &~ BUTTON_STATE_OVER;
			
			updateButton();
		}
		
		private function stageResize(e:Event):void
		{
			updateSize();
		}
		
		private function stageMouse(e:MouseEvent):void
		{
			switch (e.type) {
				case MouseEvent.MOUSE_DOWN:
					if (e.buttonDown) buttonState = buttonState | BUTTON_STATE_DOWN;
					break;
				case MouseEvent.MOUSE_UP:
					buttonState = buttonState &~ BUTTON_STATE_DOWN;
					break;
				case MouseEvent.MOUSE_OVER:
					buttonState = buttonState | BUTTON_STATE_OVER;
					break;
				case MouseEvent.MOUSE_OUT:
					buttonState = buttonState &~ BUTTON_STATE_OVER;
			}
			
			updateButton();
		}
		
		private function updateSize():void
		{
			buttonCursorSprite.width = stage.stageWidth;
			buttonCursorSprite.height = stage.stageHeight;
		}
		
		private function initButton():void
		{
			if (options.buttonImage) {
				buttonLoader.load(new URLRequest(options.buttonImage));
			} else {
				buttonLoader.unload();
			}
			
			updateSize();
			
			updateButton();
		}
		
		private function updateButton():void
		{
			var to_y:int = 0;
			var event:String = 'Leave';
			
			if (buttonState & BUTTON_STATE_DISABLED) {
				to_y = stage.stageHeight * -3;
				event = 'Disable';
			} else if (buttonState & BUTTON_STATE_DOWN) {
				to_y = stage.stageHeight * -2;
				event = 'Down';
			} else if (buttonState & BUTTON_STATE_OVER) {
				to_y = stage.stageHeight * -1;
				event = 'Enter';
			}
			
			if (to_y != buttonLoader.y) {
				buttonLoader.y = to_y;
				fireEvent('button' + event);
			}
		}
		
		private function browse():void
		{
			var filter:Array = new Array();
			
			if (options.typeFilter is String) {
				var description:String = options.typeFilterDescription || options.typeFilter;
				var type:FileFilter = new FileFilter(description, options.typeFilter + '; ' + options.typeFilter.toUpperCase() + '; ' + options.typeFilter.toLowerCase());
				filter.push(type);
			} else if (options.typeFilter is Object) {
				for (var key:String in options.typeFilter) {
					filter.push(new FileFilter(key, options.typeFilter[key] + '; ' + options.typeFilter[key].toUpperCase() + '; ' + options.typeFilter[key].toLowerCase()));
				}
			}
			
			fireEvent('browse');
			
			dialog = (options.multiple) ? new FileReferenceList() : new FileReference();
			dialog.addEventListener(Event.SELECT, handleSelect);
			dialog.addEventListener(Event.CANCEL, handleCancel);
			
			try {
				dialog.browse((filter.length) ? filter : null);
			} catch (e:Error) {
				verboseLog('Main::browse Exception', e.toString());
			}
		}
		
		private function handleSelect(event:Event):void
		{
			verboseLog('Main::handleSelect Adding Files');
			
			var added:Array = new Array();
			
			if (options.multiple) {
				var refList:FileReferenceList = dialog;
				for (var i:uint = 0; i < refList.fileList.length; i++) {
					var origin:FileReference = refList.fileList[i];
					var ref:File = new File(this, origin);
					added.push(ref);
				}
			} else {
				var origin:FileReference = dialog;
				var ref:File = new File(this, origin);
				added.push(ref);
			}
			
			var failed:Array = new Array();
			added = added.filter(function(ref:File, i:uint, self:Array) {
				if (!ref.validate()) {
					ref.id = 0; // invalidate file reference
					failed.push(ref);
					return false;
				}
				size += ref.reference.size;
				return true;
			});
			
			fileList = fileList.concat(added);
			
			fireEvent('select', [File.exportMany(added), File.exportMany(failed), queueUpdate()]);
			
			dialog = null;
		}
		
		private function handleCancel(event:Event):void
		{
			buttonState = buttonState & ~ BUTTON_STATE_OVER;
			updateButton();
			
			fireEvent('cancel');
			
			dialog = null;
		}
		
		private function getFileById(id:uint):File
		{
			if (id > 0) {
				for (var i:uint = 0; i < fileList.length; i++) {
					if (fileList[i].id == id) return fileList[i];
				}
			}
			
			verboseLog('Main::getFileById', 'File not found: ' + id);
			
			return null;
		}
		
		public function hasFile(check:File):Boolean
		{
			verboseLog('Main::hasFile', 'Checking ' + check.reference.name);
			
			return fileList.some(function(current:File, i:uint, self:Array) {
				if (current.reference == check.reference) return true;
				return (check.reference.name == current.reference.name && check.reference.size == current.reference.size && check.reference.creationDate.valueOf() == current.reference.creationDate.valueOf());
			}, this);
		}
		
		// Misc. helpers
		
		public function verboseLog(labelName:String, message:* = null):void
		{
			if (!options.verbose) return;
			if (message) ExternalInterface.call('Swiff.Uploader.log', labelName + ':', Escaper.escape(message));
			else ExternalInterface.call('Swiff.Uploader.log', labelName);
		}
		
	}
}
