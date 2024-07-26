
window.onload = () => {

    // Инициализируем html элементы
    const svg = document.getElementById('svgcanvas');
    const trash = document.getElementById('trash');
    const broom = document.getElementById('broom');

    var posX = [],
        posY = [],
        curElement = null,
        svgRect
    
    window.addEventListener("resize", (e) => {
        adjustToolSize();
    });   

    adjustToolSize();
    showDeleteButton();

    // при нажатии на мышь
    svg.addEventListener("mousedown", (e) => {
        e.preventDefault();
        svg.onmousemove = (e) => recordMousePos(e);
    });

    // касание экрана сенсорного экрана
    svg.addEventListener("touchstart", (e) => {
        e.preventDefault();
        unselectAll();
        svg.ontouchmove = (e) => recordMousePos(e);
    });

    // когда мышь отпущена
    svg.addEventListener("mouseup", () => stopDrawing());
    svg.addEventListener("touchend", () => stopDrawing());

    svg.addEventListener("click", (event) => {
        unselectAll();
        svg.ontouchmove = (e) => recordMousePos(e);
    })

    // при нажатии на пробел
    document.addEventListener("keydown", (e) => {
        if(e.code == "Space") {
            clearCanvas();
        }
    })

    // при нажании на индикатор
    trash.addEventListener("click", () => clearCanvas());
    broom.addEventListener("click", () => clearCanvas());

    // снять выделение с выбранноги ранее элемента
    function unselectAll() {
        if (event.target.id == 'svgcanvas') {curElement = null;}
        singleOutCurElement();
        showDeleteButton();
    }

    // добавляем позиции X и Y мыши в массивы arrayX и arrayY
    function recordMousePos(e) {
        let curPos;
        if (e.type == 'touchmove'){
            curPos= e.touches[0];
        } else if (e.type == 'mousemove'){
            curPos= e;
        }

        posX.push(curPos.offsetX);
        posY.push(curPos.offsetY);
        
    }

    function drawSVGLine() {
        if (posX.length == 0 || posY.length == 0) return;
        if (Math.abs(posX[0] - posX.at(-1)) < 2
            && Math.abs(posY[0] - posY.at(-1)) < 2) return;

        fetch( paint_get_figure_url , {
              method: 'POST',
              headers: {
                      'Content-Type': 'application/json;charset=utf-8'
                    },
              body: JSON.stringify({x: posX, y: posY})
        })
        .then((response) => response.json())
        .then(function(json) {
            svg.innerHTML += json.fig;
        });
        
        const content = `
          <g class="deletable">
            <line class="deletable line"
                x1="${posX[0]}" y1="${posY[0]}"
                x2="${posX.at(-1)}" y2="${posY.at(-1)}"
                stroke="red"
                stroke-width="5"
                />
            <line
                x1="${posX[0]}" y1="${posY[0]}"
                x2="${posX.at(-1)}" y2="${posY.at(-1)}"
                stroke="green"
                stroke-width="20"
                stroke-opacity="0"/>
          </g>
        `;
        svg.innerHTML += content;
        collectElements();
    }

    function drawSVGPolyLine() {}
    function drawSVGQuadratiLine() {}
    function drawSVGCubicLine() {}

    // назначить обработчики событий для всех добавленных элементов
    function collectElements() {
        let deletableElements = svg.getElementsByClassName("deletable");
        for (let dE of deletableElements) {
            dE.addEventListener("click", (event) => {
                wideLine = event.target;
                curElement = wideLine.parentElement.querySelector(".line");
                singleOutCurElement();
                showDeleteButton();
            })
            dE.addEventListener("touchstart", (event) => {
                wideLine = event.target;
                curElement = wideLine.parentElement.querySelector(".line");
                singleOutCurElement();
                showDeleteButton();
            })
        }
    }

    // выделить выбранный элемент
    function singleOutCurElement() {
        let deletableElements = svg.getElementsByClassName("deletable");
        for (let dE of deletableElements) {
            for (let ch of dE.getElementsByClassName('line')) {
                ch.setAttribute("stroke-width", "5");
            }
        }
        if (curElement !== null) {
            curElement.setAttribute("stroke-width", "8");
        }
    }

    function showDeleteButton() {
        if (curElement !== null) {
            trash.style.visibility = "hidden";
            broom.style.visibility = "visible";
        } else {
            trash.style.visibility = "visible";
            broom.style.visibility = "hidden";
        }
    }

    // очистить холст
    function clearCanvas() {
        if (curElement !== null) {
            curElement.parentElement.remove();
            curElement = null;
        } else {
            let deletableElements = svg.getElementsByClassName("deletable");
            while (deletableElements.length > 0) {
                deletableElements[0].remove();
            }
        }
        showDeleteButton();
    }

    // остановка рисования
    function stopDrawing() {
        
        drawSVGLine();
        svg.onmousemove = null;
        posX = [];
        posY = [];
    }
    
    function adjustToolSize() {
        const portrait = window.matchMedia("(orientation: portrait)").matches;
        const tools = document.getElementById("tools");
        if (tools !== null) {
            if (portrait) {
                tools.classList.add("tools-height");
                tools.classList.remove("tools-width");
            } else {
                tools.classList.add("tools-width");
                tools.classList.remove("tools-height");
            }
        }
        
        let toolButtons = document.getElementsByClassName("tool");
        if (portrait) {
            for (let tool of toolButtons) {
                tool.classList.add("tool-height");
                tool.classList.remove("tool-width");
            }
        } else {
            for (let tool of toolButtons) {
                tool.classList.add("tool-width");
                tool.classList.remove("tool-height");
            }
        }
        svgRect = svg.getBoundingClientRect();
    }
}
