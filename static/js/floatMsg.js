function elem_alt(block, tagName, alt, pos) {
    (typeof block == 'string') ? this.block = document.getElementById(block) : this.block = block;
    this.elems = this.block.getElementsByTagName(tagName);
    this.alt = alt;
    this.pos = parseInt(pos);
    this.load();
}

elem_alt.prototype = {
    load: function () {
        if (!this.div) {
            var div = document.createElement('div');
            div.setAttribute('style', 'border:1px solid #f60; background:#fff; width:160px; padding:5px; font-family:Arial; font-size:12px; position:absolute; filter:alpha(opacity=60); opacity:0.9; visibility:hidden;');
            div.style.cssText = 'border:1px solid #f60; background:#fff; width:160px; padding:5px; font-family:Arial; font-size:12px; position:absolute; filter:alpha(opacity=60); opacity:0.9; visibility:hidden;';
            this.div = div;
            div = null;
            document.body.appendChild(this.div);
        }
        var elems = this.elems
        var obj = this;
        for (var i = 0; i < elems.length; i++) {
            elems[i].onmouseover = function () {
                obj.div.innerHTML = this.getAttribute(obj.alt);
                this.setAttribute(obj.alt, '');
                obj.div_v();
            }
            elems[i].onmouseout = function () {
                obj.div_h(this);
            }
        }
    },
    div_v: function () {
        var obj = this;
        document.onmousemove = function (e) {
            var e = obj.getEvent(e);
            (e.x + obj.div.offsetWidth + obj.pos) > document.body.clientWidth ? obj.div.style.left = (e.x - obj.div.offsetWidth) + 'px' : obj.div.style.left = e.x + obj.pos + 'px';
            (e.y + obj.div.offsetHeight + obj.pos) > document.body.clientHeight ? obj.div.style.top = (e.y - obj.div.offsetHeight) + 'px' : obj.div.style.top = e.y + obj.pos + 'px';
            obj.div.style.visibility = 'visible';
        }
    },
    div_h: function (elem) {
        this.div.style.visibility = 'hidden';
        elem.setAttribute(this.alt, this.div.innerHTML);
        document.onmousemove = null;
    },
    getEvent: function (e) {
        return window.event ? {x: event.clientX, y: event.clientY} : {x: e.pageX, y: e.pageY};
    }
};
