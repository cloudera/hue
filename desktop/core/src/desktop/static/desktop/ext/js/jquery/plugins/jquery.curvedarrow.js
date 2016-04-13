(function($){
    $.fn.curvedArrow = function(options){
        var settings = $.extend({
            p0x: 50,
            p0y: 50,
            p1x: 70,
            p1y: 10,
            p2x: 100,
            p2y: 100,
            size: 30,
            lineWidth: 10,
            strokeStyle: 'rgb(245,238,49)'
        }, options);
        
        var canvas = document.createElement('canvas');
        $(canvas).appendTo(this);
        
        var x_min_max = quadraticCurveMinMax(settings.p0x, settings.p1x, settings.p2x);
        var y_min_max = quadraticCurveMinMax(settings.p0y, settings.p1y, settings.p2y);
        var padding = settings.size - settings.lineWidth;

        var x_min = x_min_max[0] - padding;
        var x_max = x_min_max[1] + padding;
        var y_min = y_min_max[0] - padding;
        var y_max = y_min_max[1] + padding;

        var p0x = settings.p0x - x_min;
        var p0y = settings.p0y - y_min;
        var p1x = settings.p1x - x_min;
        var p1y = settings.p1y - y_min;
        var p2x = settings.p2x - x_min;
        var p2y = settings.p2y - y_min;

        canvas.style.position = 'absolute';
        canvas.style.top = y_min + 'px';
        canvas.style.left = x_min + 'px';
        canvas.width = x_max - x_min;
        canvas.height = y_max - y_min;


        var ctx = canvas.getContext('2d');
        
        // Styling
        ctx.strokeStyle = settings.strokeStyle;
        ctx.lineWidth = settings.lineWidth;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';

        // Arrow body
        ctx.beginPath();
        ctx.moveTo(p0x, p0y);
        ctx.quadraticCurveTo(p1x, p1y, p2x, p2y);
        ctx.stroke();
        
        // Arrow head
        var angle = Math.atan2(p2y - p1y, p2x - p1x);
        ctx.translate(p2x, p2y);
        
        // Right side
        ctx.rotate(angle + 1);
        ctx.beginPath();
        ctx.moveTo(0, settings.size);
        ctx.lineTo(0, 0);
        ctx.stroke();
        
        // Left side
        ctx.rotate(-2);
        ctx.lineTo(0, -settings.size);
        ctx.stroke();

        // Restore context
        ctx.rotate(1 - angle);
        ctx.translate(-p2x, -p2y);

        return $(canvas).addClass('curved_arrow');
    }

    function quadraticCurveMinMax(p0, p1, p2){
        var min = p0;
        var max = p2;
        var t_step = 0.0001;
        for (var t=t_step; t <= 1; t += t_step){
            var f = (1 - t) * (1 - t) * p0 + 2 * (1 - t) * t * p1 + (t * t * p2);
            if (f < min) min = f;
            if (f > max) max = f;
        }
        return [Math.round(min), Math.round(max)];
    }
}(jQuery));
