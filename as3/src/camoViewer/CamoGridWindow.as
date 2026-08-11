package camoViewer {
  import net.wg.infrastructure.base.AbstractWindowView;
  import net.wg.gui.components.controls.Image;
  import flash.text.TextField;
  import flash.text.TextFormat;
  import flash.display.Shape;
  import flash.display.Sprite;
  import flash.events.MouseEvent;
  import flash.events.Event;
  import flash.geom.Rectangle;

  public class CamoGridWindow extends AbstractWindowView {

    private static const COLUMNS:int = 6;
    private static const CELL_SIZE:int = 96;
    private static const PADDING:int = 12;
    private static const FILTER_BAR_HEIGHT:int = 30;
    private static const VIEWPORT_HEIGHT:int = 450;
    private static const WHEEL_STEP:int = 40;
    private static const CELL_COLOR:uint = 0x2a2f36;
    private static const CELL_HOVER_COLOR:uint = 0x3a4451;
    private static const BORDER_COLOR:uint = 0x3d4451;
    private static const APPLIED_BORDER_COLOR:uint = 0xd9a441;
    private static const WINDOW_MARGIN_RIGHT:int = 20;
    private static const WINDOW_Y:int = 100;
    private static const FAVORITE_ON_COLOR:uint = 0xffd23f;
    private static const FAVORITE_OFF_COLOR:uint = 0xe5e9f0;

    private static const SEASON_WINTER:int = 1;
    private static const SEASON_SUMMER:int = 2;
    private static const SEASON_DESERT:int = 4;
    private static const FAVORITES_ONLY:int = -1;

    public var py_selectItem:Function;
    public var py_toggleFavorite:Function;

    private var content:Sprite;
    private var scrollY:Number = 0;
    private var contentHeight:Number = 0;

    private var allItems:Array = [];
    private var favoritesButton:FilterButton;
    private var seasonButtons:Array = [];
    private var favoritesOnly:Boolean = false;
    private var seasonFilter:int = 0;

    public function CamoGridWindow() {
      super();
    }

    override protected function onPopulate():void {
      super.onPopulate();
      window.title = 'camo-viewer';
      width = COLUMNS * CELL_SIZE + PADDING * 2;
      height = FILTER_BAR_HEIGHT + VIEWPORT_HEIGHT + PADDING * 2;
      as_setGeometry(App.appWidth - width - WINDOW_MARGIN_RIGHT, WINDOW_Y, width, height);

      var bg:Shape = new Shape();
      bg.graphics.beginFill(0x1b1f24);
      bg.graphics.drawRect(0, 0, width, height);
      bg.graphics.endFill();
      addChild(bg);
      bg.addEventListener(MouseEvent.MOUSE_WHEEL, onMouseWheel, false, 0, true);

      buildFilterBar();

      content = new Sprite();
      content.x = PADDING;
      content.y = PADDING + FILTER_BAR_HEIGHT;
      content.scrollRect = new Rectangle(0, 0, COLUMNS * CELL_SIZE, VIEWPORT_HEIGHT);
      addChild(content);
      content.addEventListener(MouseEvent.MOUSE_WHEEL, onMouseWheel, false, 0, true);
    }

    private function buildFilterBar():void {
      var buttonY:int = PADDING;
      var buttonX:int = PADDING;
      var gap:int = 4;

      favoritesButton = new FilterButton('Favorites', FAVORITES_ONLY);
      favoritesButton.x = buttonX;
      favoritesButton.y = buttonY;
      favoritesButton.addEventListener(MouseEvent.CLICK, onFavoritesButtonClick);
      addChild(favoritesButton);
      buttonX += 76 + gap;

      var seasons:Array = [
        {label: 'All', value: 0},
        {label: 'Summer', value: SEASON_SUMMER},
        {label: 'Winter', value: SEASON_WINTER},
        {label: 'Desert', value: SEASON_DESERT}
      ];
      var i:int;
      for (i = 0; i < seasons.length; i++) {
        var btn:FilterButton = new FilterButton(seasons[i].label, seasons[i].value);
        btn.x = buttonX;
        btn.y = buttonY;
        btn.addEventListener(MouseEvent.CLICK, onSeasonButtonClick);
        addChild(btn);
        seasonButtons.push(btn);
        buttonX += 76 + gap;
      }
      seasonButtons[0].setActive(true);
    }

    public function as_showSeasonFilter(value:Boolean):void {
      var i:int;
      for (i = 0; i < seasonButtons.length; i++) {
        seasonButtons[i].visible = value;
      }
      if (!value && seasonFilter != 0) {
        seasonFilter = 0;
        seasonButtons[0].setActive(true);
        applyFilters();
      }
    }

    private function onFavoritesButtonClick(event:MouseEvent):void {
      favoritesOnly = !favoritesOnly;
      favoritesButton.setActive(favoritesOnly);
      applyFilters();
    }

    private function onSeasonButtonClick(event:MouseEvent):void {
      var clicked:FilterButton = FilterButton(event.currentTarget);
      seasonFilter = clicked.value;
      var i:int;
      for (i = 0; i < seasonButtons.length; i++) {
        seasonButtons[i].setActive(seasonButtons[i] == clicked);
      }
      applyFilters();
    }

    private function applyFilters():void {
      var visible:Array = [];
      var i:int;
      for (i = 0; i < allItems.length; i++) {
        var item:Object = allItems[i];
        if (favoritesOnly && !item.favorite) {
          continue;
        }
        if (seasonFilter != 0 && (int(item.season) & seasonFilter) == 0) {
          continue;
        }
        visible.push(item);
      }
      rebuildGrid(visible);
    }

    private function onMouseWheel(event:MouseEvent):void {
      var maxScroll:Number = Math.max(0, contentHeight - VIEWPORT_HEIGHT);
      scrollY = Math.max(0, Math.min(maxScroll, scrollY - event.delta * WHEEL_STEP / 3));
      var rect:Rectangle = content.scrollRect;
      rect.y = scrollY;
      content.scrollRect = rect;
    }

    public function as_setItems(items:Array):void {
      allItems = items;
      applyFilters();
    }

    private function rebuildGrid(items:Array):void {
      while (content.numChildren > 0) {
        content.removeChildAt(0);
      }
      scrollY = 0;
      var rect:Rectangle = content.scrollRect;
      rect.y = 0;
      content.scrollRect = rect;

      var i:int;
      for (i = 0; i < items.length; i++) {
        addCell(items[i], i);
      }

      var rows:int = Math.ceil(items.length / COLUMNS);
      contentHeight = rows * CELL_SIZE;
    }

    private function addCell(item:Object, index:int):void {
      var col:int = index % COLUMNS;
      var row:int = int(index / COLUMNS);
      var x:int = col * CELL_SIZE;
      var y:int = row * CELL_SIZE;

      var cell:GridCell = new GridCell();
      cell.x = x;
      cell.y = y;
      cell.buttonMode = true;
      cell.intCD = Number(item['intCD']);
      cell.applied = Boolean(item['applied']);
      cell.favorite = Boolean(item['favorite']);
      drawCellBackground(cell, CELL_COLOR);
      cell.addEventListener(MouseEvent.CLICK, onCellClick);
      cell.addEventListener(MouseEvent.MOUSE_OVER, onCellOver);
      cell.addEventListener(MouseEvent.MOUSE_OUT, onCellOut);
      content.addChild(cell);

      var iconSource:String = String(item['icon']);
      if (iconSource != '' && iconSource != 'null' && iconSource != 'undefined') {
        var icon:Image = new Image();
        icon.x = 4;
        icon.y = 4;
        icon.mouseEnabled = false;
        icon.addEventListener(Event.CHANGE, onIconChange, false, 0, true);
        icon.source = iconSource;
        cell.addChild(icon);
      }

      var label:TextField = new TextField();
      label.width = CELL_SIZE - 14;
      label.height = CELL_SIZE - 66;
      label.wordWrap = true;
      label.selectable = false;
      label.mouseEnabled = false;
      label.x = 4;
      label.y = 64;
      label.text = String(item['name']);

      var fmt:TextFormat = new TextFormat();
      fmt.color = 0x9aa5b1;
      fmt.size = 11;
      label.setTextFormat(fmt);
      label.defaultTextFormat = fmt;

      cell.addChild(label);

      var star:Sprite = new Sprite();
      star.x = CELL_SIZE - 20;
      star.y = 12;
      drawStar(star, cell.favorite);
      star.addEventListener(MouseEvent.CLICK, onStarClick, false, 0, true);
      cell.addChild(star);
    }

    private function drawStar(star:Sprite, favorite:Boolean):void {
      var color:uint = favorite ? FAVORITE_ON_COLOR : FAVORITE_OFF_COLOR;
      star.graphics.clear();

      // Invisible hit-area, larger than the drawn star for an easier click target.
      star.graphics.beginFill(0x000000, 0);
      star.graphics.drawRect(-9, -9, 18, 18);
      star.graphics.endFill();

      // Soft dark backing so the star stays legible over bright icon thumbnails.
      star.graphics.beginFill(0x000000, 0.4);
      star.graphics.drawCircle(0, 0, 8);
      star.graphics.endFill();

      if (favorite) {
        star.graphics.beginFill(color);
      } else {
        star.graphics.lineStyle(1.6, color);
      }
      var outerR:Number = 7;
      var innerR:Number = 3;
      var points:int = 5;
      var i:int;
      for (i = 0; i <= points * 2; i++) {
        var angle:Number = (Math.PI / points) * i - Math.PI / 2;
        var r:Number = (i % 2 == 0) ? outerR : innerR;
        var px:Number = Math.cos(angle) * r;
        var py:Number = Math.sin(angle) * r;
        if (i == 0) {
          star.graphics.moveTo(px, py);
        } else {
          star.graphics.lineTo(px, py);
        }
      }
      if (favorite) {
        star.graphics.endFill();
      }
    }

    private function onStarClick(event:MouseEvent):void {
      event.stopPropagation();
      var star:Sprite = Sprite(event.currentTarget);
      var cell:GridCell = GridCell(star.parent);
      if (py_toggleFavorite != null) {
        cell.favorite = Boolean(py_toggleFavorite(cell.intCD));
        drawStar(star, cell.favorite);
        updateStoredFavorite(cell.intCD, cell.favorite);
        if (favoritesOnly && !cell.favorite) {
          applyFilters();
        }
      }
    }

    private function updateStoredFavorite(intCD:Number, favorite:Boolean):void {
      var i:int;
      for (i = 0; i < allItems.length; i++) {
        if (Number(allItems[i].intCD) == intCD) {
          allItems[i].favorite = favorite;
          return;
        }
      }
    }

    private function onIconChange(event:Event):void {
      var icon:Image = Image(event.target);
      icon.width = CELL_SIZE - 14;
      icon.height = 56;
    }

    private function drawCellBackground(cell:GridCell, color:uint):void {
      var borderColor:uint = cell.applied ? APPLIED_BORDER_COLOR : BORDER_COLOR;
      var borderWidth:Number = cell.applied ? 2 : 1;
      cell.graphics.clear();
      cell.graphics.beginFill(color);
      cell.graphics.lineStyle(borderWidth, borderColor);
      cell.graphics.drawRect(0, 0, CELL_SIZE - 6, CELL_SIZE - 6);
      cell.graphics.endFill();
    }

    private function onCellOver(event:MouseEvent):void {
      drawCellBackground(GridCell(event.currentTarget), CELL_HOVER_COLOR);
    }

    private function onCellOut(event:MouseEvent):void {
      drawCellBackground(GridCell(event.currentTarget), CELL_COLOR);
    }

    private function onCellClick(event:MouseEvent):void {
      var cell:GridCell = GridCell(event.currentTarget);
      if (py_selectItem != null) {
        py_selectItem(cell.intCD);
      }
    }
  }
}
