package camoViewer {
  import net.wg.infrastructure.base.AbstractWindowView;
  import flash.text.TextField;
  import flash.text.TextFormat;
  import flash.display.Shape;

  public class CamoViewerTestWindow extends AbstractWindowView {

    public var py_close:Function;

    public function CamoViewerTestWindow() {
      super();
    }

    override protected function onPopulate():void {
      super.onPopulate();
      width = 400;
      height = 300;
      window.title = 'camo-viewer Phase 2 test';

      var bg:Shape = new Shape();
      bg.graphics.beginFill(0x1b1f24);
      bg.graphics.drawRect(0, 0, width, height);
      bg.graphics.endFill();
      addChild(bg);

      var label:TextField = new TextField();
      label.text = 'Hello from a real compiled Scaleform view.';
      label.autoSize = 'left';
      label.x = 16;
      label.y = 16;
      label.selectable = false;

      var fmt:TextFormat = new TextFormat();
      fmt.color = 0xe8e8e8;
      fmt.size = 16;
      label.setTextFormat(fmt);
      label.defaultTextFormat = fmt;

      addChild(label);
    }

    override protected function onDispose():void {
      super.onDispose();
    }
  }
}
