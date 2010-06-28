/**
 * Swiff.Uploader Class File
 *
 * @licence		MIT Licence
 *
 * @author		Harald Kirschner <http://digitarald.de>
 * @copyright	Authors
 */

package
{
	import flash.events.*;
	import flash.net.FileReference;
	import flash.net.FileFilter;
	import flash.utils.Timer;

	import flash.net.URLRequest;
	import flash.net.URLRequestMethod;
	import flash.net.URLVariables;
	
	/**
	 * @author Harald Kirschner <mail [at] digitarald.de>
	 */
	public class File
	{
		static var idStack:uint = 1;
		
		static const STATUS_QUEUED:uint = 0;
		static const STATUS_RUNNING:uint = 1;
		static const STATUS_ERROR:uint = 2;
		static const STATUS_COMPLETE:uint = 3;
		static const STATUS_STOPPED:uint = 4;

		public var id:uint = 0;
		
		public var status:uint = 0;

		private var options:Object = {
			url: null,
			method: null,
			data: null,
			mergeData: null,
			fieldName: null
		}
		
		public var reference:FileReference = null;
		private var parent:Main = null;
		
		public var responseText:String = null;
		public var responseCode:uint = 0;
		public var responseError:String = null;
		
		public var validationError:String = null;
		
		public var addDate:Date = null;
		public var startDate:Date = null;
		eublic var progressDate:Date = null;
		public var completeDate:Date = null;
		
		public var fileExtension:String = null;
		
		public var bytesLoaded:uint = 0;
		public var timeElapsed:uint = 0;
		public var timeRemaining:uint = 0;
		
		public var progressGraph:Array = new Array();
		public var rate:uint = 0;
		public var rateAvg:uint = 0;
		
		private var timeout:Timer = null;
		private var lockProgress:uint = 0;
		
		public function File(parent_init:Main, reference_init:FileReference)
		{
			id = File.idStack++;
			
			reference = reference_init;
			parent = parent_init;
			
			reference.addEventListener(Event.OPEN, handleOpen);
			reference.addEventListener(ProgressEvent.PROGRESS, handleProgress);
			reference.addEventListener(DataEvent.UPLOAD_COMPLETE_DATA, handleComplete);
			reference.addEventListener(HTTPStatusEvent.HTTP_STATUS, handleHttpStatus);
			reference.addEventListener(IOErrorEvent.IO_ERROR, handleIoError);
			reference.addEventListener(SecurityErrorEvent.SECURITY_ERROR, handleSecurityError);
			
			fileExtension = reference.name.replace(/.+\.([^.]+)$/, '$1').toLowerCase();
			
			addDate = new Date();
			
			if (parent.options.timeLimit) {
				timeout = new Timer(parent.options.timeLimit * 1000, 1);
				timeout.addEventListener('timer', handleTimeout);
				timeout.start();
			}
		}
		
		public function fireEvent(functionName:String, queue:Boolean = false):void
		{
			var args:Array = [export()];
			if (queue) args.push(parent.queueUpdate());
			
			parent.fireEvent('file' + functionName.charAt(0).toUpperCase() + functionName.substr(1), args);
		}
		
		private function handleOpen(event:Event):void
		{
			progressDate = startDate = new Date();
			
			if (timeout) timeout.start();
			
			fireEvent('open');
		}
		
		private function handleProgress(event:ProgressEvent):void
		{
			if (timeout) {
				timeout.reset();
				timeout.start();
			}
			
			var now:uint = new Date().getTime();
			
			var allow:Boolean = (!lockProgress || lockProgress < now - 100 || event.bytesLoaded == reference.size)
			
			if (allow) {
				updateProgress((event.bytesLoaded >= 0) ? event.bytesLoaded : 0);
				
				lockProgress = now;
				fireEvent('progress', true);
			} else {
				// parent.verboseLog('Process Skipped', [event.bytesLoaded, now - lockProgress]);
			}
			
		}
		
		private function resetProgress():void
		{
			responseText = responseError = null;
			responseCode = 0;
			
			progressGraph.length = 0;
			startDate = progressDate = completeDate = null;
			timeElapsed = timeRemaining = rate = rateAvg = bytesLoaded = 0;
		}
		
		private function updateProgress(bytes_loaded:uint, complete:Boolean = false)
		{
			var now:Date = new Date();
			var i:uint = 0, length:uint = 0;
			
			rate = rateAvg = 0;
			
			if (bytes_loaded && !complete) {
				
				var bytes_diff:Number = (bytes_loaded - bytesLoaded) / (now.getTime() - progressDate.getTime());
				length = progressGraph.unshift(Math.round(bytes_diff));
				
				bytesLoaded = bytes_loaded;

				if (length > 1) {
					
					if (length > parent.options.progressGraphSize) length = parent.options.progressGraphSize;
					
					var mean:Number = 0;
					var variance:Number = 0;
					
					for (i = 0; i < length; i++) {
						mean += progressGraph[i];
						variance += Math.pow(progressGraph[i] - mean, 2);
					}
					mean /= length;
					
					rate = rateAvg = Math.round(mean * 1000);
					
					if (length > 6) {
						var standard_dev:Number = Math.sqrt(variance / length);
						var deviation_range:Number = 2.0;
						
						var filtered_sum:Number = 0;
						var filtered_count:uint = 0;
						
						for (i = 0; i < length; i++) {
							var value:Number = (progressGraph[i] - mean) / standard_dev;
							
							if (value <= deviation_range && value >= -deviation_range) {
								filtered_sum += progressGraph[i];
								filtered_count++;
							}
						}
						
						rateAvg = Math.round(filtered_sum / filtered_count * 1000);

						timeRemaining = (reference.size - bytes_loaded) / rateAvg;
					}
				}
			}
			
			timeElapsed = (now.getTime() - startDate.getTime()) / 1000;
			
			progressDate = now;
		
			parent.rate = parent.bytesLoaded = 0;
			
			for (var i = 0; i < parent.fileList.length; i++) {
				var file:File = parent.fileList[i];
				switch (file.status) {
					case File.STATUS_RUNNING:
						parent.rate += file.rateAvg;
					case File.STATUS_COMPLETE:
						parent.bytesLoaded += file.bytesLoaded;
				}
			}
		}
		
		private function handleTimeout(event:TimerEvent):void
		{
			if (status != File.STATUS_RUNNING) return;
			
			reference.cancel();
			
			complete('timeLimit (' + options.timeLimit + 's) exceeded', 'timeout', null);
		}
		
		private function handleComplete(event:DataEvent):void
		{
			complete(event.data);
		}
		
		private function handleIoError(event:IOErrorEvent):void
		{
			complete(event.text, event.type, null);
		}
		
		private function handleSecurityError(event:SecurityErrorEvent):void
		{
			complete(event.text, event.type, null);
		}
		
		private function handleHttpStatus(event:HTTPStatusEvent):void
		{
			if (parent.options.passStatus is Array) {
				var list:Array = parent.options.passStatus;
				if (list.length && list.indexOf(event.status) != -1) {
					complete(null, null, event.status);
					return;
				}
			}
			
			complete(null, event.type, event.status);
		}
		
		private function complete(text:String = null, error:String = null, code:int = 0)
		{
			if (status != File.STATUS_RUNNING) {
				parent.verboseLog('File[' + id + ']::complete wasted!', [].concat(arguments));
				return;
			}
			
			if (timeout) timeout.reset();
									
			completeDate = new Date();
			
			responseText = text;
			responseCode = code;
			
			if (error) {
				responseError = error;
				status = File.STATUS_ERROR;
			} else {
				status = File.STATUS_COMPLETE;
			}
			
			parent.uploading--;
			
			updateProgress(reference.size, true);
			
			fireEvent('complete', true);
			
			parent.checkQueue(true);
		}
		
		public function setOptions(options_init:Object = null):void
		{
			if (options_init != null) {
				for (var prop:String in options) {
					if (options_init.hasOwnProperty(prop)) options[prop] = options_init[prop];
				}
			}
		}
		
		public function start():Boolean
		{
			if (status == File.STATUS_RUNNING) return false;
			
			var options_parent:Object = parent.options;
			var merged:Object = new Object();
			
			for (var prop:String in options) {
				merged[prop] = (options[prop] != null) ? options[prop] : options_parent[prop];
			}
			
			try {
				var url_request:URLRequest = new URLRequest(merged.url || '');
				
				if (merged.data != null && merged.data != false) {
					if (merged.mergeData && options.data && options_parent.data) {
						if (options.data is String && options_parent.data is String) {
							merged.data = options_parent.data + '&' + options.data;
						} else {
							merged.data = new Object();
							for (var prop:String in options_parent.data) {
								merged.data[prop] = options_parent.data[prop];
							}
							for (var prop:String in options.data) {
								merged.data[prop] = options.data[prop];
							}
						}
					}
					
					var data:URLVariables = new URLVariables();
					if (merged.data is String) data.decode(merged.data);
					else for (var key:Object in merged.data) data[key] = merged.data[key];
					url_request.data = data;
				}
			
				url_request.method = URLRequestMethod[(merged.method) ? merged.method.toUpperCase() : 'POST'];
			} catch (e:Error) {
				parent.verboseLog('File[' + id + ']::start - Exception (URLRequest)', String(e));
				return false;
			}
			
			parent.verboseLog('File[' + id + ']::start', merged);
			
			resetProgress();
			
			status = File.STATUS_RUNNING;
			parent.uploading++;
			
			fireEvent('start', true);
			
			try {
				reference.upload(url_request, merged.fieldName || 'Filedata');
			} catch (e:Error) {
				parent.verboseLog('File[' + id + ']::start - Exception (upload)', String(e));
				stop();
				return false;
			}
			
			return true;
		}
		
		public function stop(eventful:Boolean = true):Boolean
		{
			if (status != File.STATUS_RUNNING) return false;
			
			if (timeout) timeout.reset();
			
			reference.cancel();
			status = File.STATUS_STOPPED;
			
			parent.uploading--;
			parent.bytesLoaded -= bytesLoaded;
			parent.rate -= rateAvg;
			
			resetProgress();
			
			if (eventful) {
				fireEvent('stop', true);
				parent.checkQueue(true);
			}
			
			return true;
		}
		
		public function requeue():Boolean
		{
			var running:Boolean = stop(false);
			
			status = File.STATUS_QUEUED;
			
			fireEvent('requeue');
			
			if (running) parent.checkQueue(true);
			
			return true;
		}
		
		public function remove():Boolean
		{
			var running:Boolean = stop(false);
			
			var idx = parent.fileList.indexOf(this);
			parent.fileList.splice(idx, 1);

			parent.size -= reference.size;
				
			fireEvent('remove', true);
			
			if (running) parent.checkQueue(true);
			
			reference = null;
			
			return true;
		}
		
		public function validate():Boolean
		{
			if (!parent.options.allowDuplicates && parent.hasFile(this)) {
				validationError = 'duplicate';
				return false;
			}

			if (parent.options.fileSizeMin > 0 && reference.size < parent.options.fileSizeMin) {
				validationError = 'sizeLimitMin';
				return false;
			}
			
			if (parent.options.fileSizeMax > 0 && reference.size > parent.options.fileSizeMax) {
				validationError = 'sizeLimitMax';
				return false;
			}
			
			return true;
		}
		
		public function export():Object
		{
			var export:Object = {
				id: id,
				name: reference.name,
				size: reference.size,
				modificationDate: reference.modificationDate,
				creationDate: reference.creationDate,
				extension: fileExtension,
				status: status,
				validationError: validationError,
				addDate: addDate
			};
			
			if (startDate) {
				export.startDate = startDate;
				export.progressDate = progressDate;
				
				export.progress = {
					graph: progressGraph,
					bytesLoaded: bytesLoaded,
					percentLoaded: Math.ceil(bytesLoaded / reference.size * 100),
					rate: rate,
					rateAvg: rateAvg,
					timeElapsed: timeElapsed,
					timeRemaining: timeRemaining
				};
			};
			
			if (completeDate) {
				export.completeDate = completeDate;
				
				export.response = {
					text: responseText,
					code: responseCode,
					error: responseError
				}
			}
			
			return export;
		}
		
		// Static methods
		
		static public function exportMany(files:Array):Array
		{
			if (!files.length) return null;
			
			return files.map(function(current:File, i:uint, self:Array) {
				return current.export();
			});
		}

	}
	
}
