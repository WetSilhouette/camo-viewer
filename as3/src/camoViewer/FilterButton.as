package camoViewer {
  import flash.display.Sprite;
  import flash.text.TextField;
  import flash.text.TextFormat;

  public class FilterButton extends Sprite {

    private static const WIDTH:Number = 76;
    private static const HEIGHT:Number = 22;
    private static const OFF_COLOR:uint = 0x2a2f36;
    private static const ON_COLOR:uint = 0x4a6a8a;
    private static const BORDER_COLOR:uint = 0x3d4451;
    private static const TEXT_OFF:uint = 0x9aa5b1;
    private static const TEXT_ON:uint = 0xe5e9f0;

    public var value:int;
    public var active:Boolean = false;

    private var label:TextField;

    public function FilterButton(text:String, buttonValue:int) {
      super();
      value = buttonValue;
      buttonMode = true;

      label = new TextField();
      label.width = WIDTH;
      label.height = HEIGHT;
      label.selectable = false;
      label.mouseEnabled = false;
      label.text = text;

      var fmt:TextFormat = new TextFormat();
      fmt.align = 'center';
      fmt.size = 11;
      label.setTextFormat(fmt);
      label.defaultTextFormat = fmt;
      addChild(label);

      redraw();
    }

    public function setActive(value:Boolean):void {
      active = value;
      redraw();
    }

    private function redraw():void {
      graphics.clear();
      graphics.beginFill(active ? ON_COLOR : OFF_COLOR);
      graphics.lineStyle(1, BORDER_COLOR);
      graphics.drawRect(0, 0, WIDTH, HEIGHT);
      graphics.endFill();

      var fmt:TextFormat = new TextFormat();
      fmt.align = 'center';
      fmt.size = 11;
      fmt.color = active ? TEXT_ON : TEXT_OFF;
      label.setTextFormat(fmt);
      label.defaultTextFormat = fmt;
    }
  }
}
