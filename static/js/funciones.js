const spinner = document.getElementById("spinner");
const PATH = IS_DEV ? "/" : "/reportespyact/";
var DATA_CHART_S = "";
var DATA_CHART_C = "";
var DATA_CHART_F = "";
var DATA_CHART_CATEGORIA = "";
var DATA_FINA = "";
var TITLE_GRAFICO = "";
async function InsertData(id, text) {
  e = document.getElementById(id);
  await new Promise((r) => setTimeout(r, 500));
  e.insertAdjacentHTML("afterend", text);
  sty =
    id.substring(0, 3) === "mef"
      ? "font-weight: bold;cursor: pointer;"
      : "cursor: pointer;";
  e.style.cssText = sty;
  spinner.setAttribute("hidden", "");
  let _id = document.getElementById(id);
  _id.setAttribute("load", "off");
}
// ACTUALIZACION POR BUSQUEDAS
async function reloadedD(ubigeo, act, _amb) {
  spinner.removeAttribute("hidden");

  //Checkbox Proyecto y Actividades
  let chkPy = document.getElementById("chkAProyectos");
  let chkAc = document.getElementById("chkActividades");
  console.log();
  let StrPyAct =
    chkPy.checked && chkAc.checked ? "1" : chkPy.checked ? "2" : "3";

  //combo Año de ejecucion
  let anio = document.getElementById("cboAnio");
  let strAnio = anio.options[anio.selectedIndex].value || "";

  //combo de Funcion
  let e = document.getElementById("cbofun");
  let strFun = e.options[e.selectedIndex].value || "";

  //combo de Categoria Presupuestal
  let f = document.getElementById("cboppto");
  let strPpto = f.options[f.selectedIndex].value || "";

  let data = {
    anio: strAnio,
    ubigeo: ubigeo,
    act: StrPyAct,
    fun: strFun,
    cat: strPpto,
    sec: "",
    amb: _amb,
  };
  let params = {
    method: "post",
    body: JSON.stringify(data),
    headers: { "Content-type": "application/json" },
  };

  fetch(PATH + "nivel/", params)
    .then((res) => res.text())
    .then(async function (text) {
      await new Promise((r) => setTimeout(r, 500));
      document.getElementById("data-mef-d").innerHTML = text;
      spinner.setAttribute("hidden", "");
    }); // then log it out
}

async function reloadedF(anio, ubigeo) {
  spinner.removeAttribute("hidden");
  let nom = document.getElementById("txtPry").value;

  let cod = document.getElementById("txtCod").value;

  let data = { anio: anio, ubigeo: ubigeo, act: "", nom: nom, cod: cod };
  let params = {
    method: "post",
    body: JSON.stringify(data),
    headers: { "Content-type": "application/json" },
  };

  fetch(PATH + "nom-py", params)
    .then((res) => res.text())
    .then(async function (text) {
      document.getElementById("data-mef-d").innerHTML = text;
      spinner.setAttribute("hidden", "");
    }); // then log it out
}

function fnHidden(id, op) {
  var row = document.getElementById(id);
  var elm = row.parentNode.childElementCount;

  if (op == "e") {
    for (i = 1; i < elm; i++) {
      if (row) {
        var row = row.parentNode.rows[i];

        row.setAttribute("hidden", "");
      }
    }
  } else if (op == "s") {
    let sector = id.substring(0, 2);
    var idx = row.rowIndex;
    for (i = idx; i < elm; i++) {
      var row1 = row.parentNode.rows[i];
      if (row1.id.substring(1, 3) == sector) {
        row1.setAttribute("hidden", "");

        if (row1.getAttribute("acc") == "off" && row1.id.length > 6) {
          row1.setAttribute("acc", "on");
          fnHidden(row1.id, "j");
        }
      }
    }
  } else if (op == "p") {
    let pliego = id.substring(1, 6);
    console.log(pliego);
    var idx = row.rowIndex;
    for (i = idx; i < elm; i++) {
      var row1 = row.parentNode.rows[i];
      if (row1.id.substring(1, 6) == pliego) {
        row1.setAttribute("hidden", "");
        console.log(row1.id.length);
        if (row1.getAttribute("acc") == "off" && row1.id.length > 6) {
          console.log("borrar");
          row1.setAttribute("acc", "on");
          fnHidden(row1.id, "j");
        }
      }
    }
  } else if (op == "j") {
    var next = row.parentNode.rows[row.rowIndex];
    if (next) next.setAttribute("hidden", "");
  }
}

function fnShow(id, op) {
  var row = document.getElementById(id);
  var elm = row.parentNode.childElementCount;
  if (op == "e") {
    for (i = 1; i < elm; i++) {
      if (row) {
        var row = row.parentNode.rows[i];
        if (row.id.length <= 2 && row.id) {
          row.removeAttribute("hidden");
          row.setAttribute("acc", "on");
        }
      }
    }
  } else if (op == "s") {
    let sector = id.substring(0, 2);
    var idx = row.rowIndex;
    for (i = idx; i < elm; i++) {
      var row1 = row.parentNode.rows[i];
      if (row1.id.substring(1, 3) == sector) {
        row1.removeAttribute("hidden");
      }
    }
  } else if (op == "p") {
    let pliego = id.substring(1, 6);
    var idx = row.rowIndex;
    for (i = idx; i < elm; i++) {
      var row1 = row.parentNode.rows[i];
      if (row1.id.substring(1, 6) == pliego) {
        row1.removeAttribute("hidden");
      }
    }
  } else if (op == "j") {
    var next = row.parentNode.rows[row.rowIndex];
    next.removeAttribute("hidden");
  }
}

function reloadedCboPPTO(_anio, _ubigeo, _act) {
  let e = document.getElementById("cbofun");
  let strFun = e.options[e.selectedIndex].value || "";
  let data = { anio: _anio, ubigeo: _ubigeo, act: _act, fun: strFun };
  console.log(data);
  let params = {
    method: "post",
    body: JSON.stringify(data),
    headers: { "Content-type": "application/json" },
  };
  fetch(PATH + "funcion", params)
    .then((res) => res.text())
    .then((text) => (document.getElementById("cboppto").innerHTML = text));
}
//----------------------------------------------------------------------------------------------------------

function onclickRowNivel(
  _id,
  _anio,
  _ubigeo,
  _act,
  _nivel,
  _fun,
  _orden,
  _cat,
  _sec,
  _amb,
) {
  let id = document.getElementById(_id);
  let data = {
    orden: _orden,
    id: _id,
    anio: _anio,
    ubigeo: _ubigeo,
    act: _act,
    nivel: _nivel,
    fun: _fun,
    cat: _cat,
    sec: _sec,
    amb: _amb,
  };
  let params = {
    method: "post",
    body: JSON.stringify(data),
    headers: { "Content-type": "application/json" },
  };
  if (id.getAttribute("load") == "on") {
    spinner.removeAttribute("hidden");
    fetch(PATH + "sector", params)
      .then((res) => res.text())
      .then((text) => InsertData(_id, text));
  } else {
    if (id.getAttribute("acc") == "off") {
      fnHidden(_id, "e");
      id.setAttribute("acc", "on");
    } else {
      fnShow(_id, "e");
      id.setAttribute("acc", "off");
    }
  }
}

function onclickRowSector(
  _id,
  _anio,
  _ubigeo,
  _act,
  _nivel,
  _sector,
  _fun,
  _cat,
  _orden,
  _amb,
) {
  let id = document.getElementById(_id);
  let data = {
    id: _id,
    anio: _anio,
    ubigeo: _ubigeo,
    act: _act,
    nivel: _nivel,
    fun: _fun,
    sector: _sector,
    orden: _orden,
    cat: _cat,
    amb: _amb,
  };
  let params = {
    method: "post",
    body: JSON.stringify(data),
    headers: { "Content-type": "application/json" },
  };
  if (id.getAttribute("load") == "on") {
    spinner.removeAttribute("hidden");
    fetch(PATH + "pliego", params)
      .then((res) => res.text())
      .then((text) => InsertData(_id, text));
  } else {
    if (id.getAttribute("acc") == "off") {
      fnHidden(_id, "s");
      id.setAttribute("acc", "on");
    } else {
      fnShow(_id, "s");
      id.setAttribute("acc", "off");
    }
  }
}

function onclickRowPliego(
  _id,
  _anio,
  _ubigeo,
  _act,
  _nivel,
  _sector,
  _fun,
  _pliego,
  _cat,
  _orden,
  _amb,
) {
  let id = document.getElementById(_id);
  let data = {
    id: _id,
    anio: _anio,
    ubigeo: _ubigeo,
    act: _act,
    nivel: _nivel,
    sector: _sector,
    fun: _fun,
    pliego: _pliego,
    orden: _orden,
    cat: _cat,
    amb: _amb,
  };
  let params = {
    method: "post",
    body: JSON.stringify(data),
    headers: { "Content-type": "application/json" },
  };
  if (id.getAttribute("load") == "on") {
    spinner.removeAttribute("hidden");
    fetch(PATH + "ejecutora", params)
      .then((res) => res.text())
      .then((text) => InsertData(_id, text));
  } else {
    if (id.getAttribute("acc") == "off") {
      fnHidden(_id, "p");
      id.setAttribute("acc", "on");
    } else {
      fnShow(_id, "p");
      id.setAttribute("acc", "off");
    }
  }
}

function onclickRowEjecutora(
  _id,
  _anio,
  _ubigeo,
  _act,
  _nivel,
  _sector,
  _pliego,
  _ejecutora,
  _fun,
  _cat,
  _amb,
) {
  let id = document.getElementById(_id);
  let data = {
    id: _id,
    anio: _anio,
    ubigeo: _ubigeo,
    act: _act,
    nivel: _nivel,
    sector: _sector,
    fun: _fun,
    pliego: _pliego,
    ejecutora: _ejecutora,
    cat: _cat,
    amb: _amb,
  };
  console.log(data);
  let params = {
    method: "post",
    body: JSON.stringify(data),
    headers: { "Content-type": "application/json" },
  };
  if (id.getAttribute("load") == "on") {
    spinner.removeAttribute("hidden");
    fetch(PATH + "proyecto", params)
      .then((res) => res.text())
      .then((text) => InsertData(_id, text));
  } else {
    if (id.getAttribute("acc") == "off") {
      fnHidden(_id, "j");
      id.setAttribute("acc", "on");
    } else {
      fnShow(_id, "j");
      id.setAttribute("acc", "off");
    }
  }
}

// DATA PARA GRAFICOS
function GetDataGrafico(_tip, _ubigeo) {
  let path_grafico = _tip ? "grafico/" + _tip : "grafico-violencia";
  console.log(path_grafico);

  spinner.removeAttribute("hidden");
  var sw = 0;

  switch (_tip) {
    case "sector":
      DATA_FINA = DATA_CHART_S;
      sw = DATA_CHART_S == "" ? 1 : 0;
      TITLE_GRAFICO = "Gasto público por Sectores (2012-2020)";
      TITLE_GRAFICO_LEG = "SECTOR";
      BotonesGrafico("btnSec");
      break;
    case "cat_pre":
      DATA_FINA = DATA_CHART_C;
      sw = DATA_CHART_C == "" ? 1 : 0;
      TITLE_GRAFICO = "Gasto público por Categoría Presupuestal (2012-2020)";
      TITLE_GRAFICO_LEG = "CAT. PRESUPUESTAL";
      BotonesGrafico("btnCat");
      break;
    case "funcion":
      DATA_FINA = DATA_CHART_F;
      sw = DATA_CHART_F == "" ? 1 : 0;
      TITLE_GRAFICO = "Gasto público por Funciones (2012-2020)";
      TITLE_GRAFICO_LEG = "FUNCION";
      BotonesGrafico("btnFun");
      break;
    case "":
      DATA_FINA = DATA_CHART_CATEGORIA;
      sw = DATA_CHART_CATEGORIA == "" ? 1 : 0;
      TITLE_GRAFICO =
        "Gasto público de Lucha contra la violencia familiar (2012-2020)";
      TITLE_GRAFICO_LEG = "Nivel Gobierno";
  }
  if (sw == 1) {
    fetch(PATH + path_grafico + "/" + _ubigeo)
      .then((res) => res.json())
      .then(function (json) {
        switch (_tip) {
          case "sector":
            DATA_CHART_S = json;
            DATA_FINA = DATA_CHART_S;
            TITLE_GRAFICO = "Gasto público por Sectores (2012-2020)";
            TITLE_GRAFICO_LEG = "SECTOR";
            BotonesGrafico("btnSec");
            break;
          case "cat_pre":
            DATA_CHART_C = json;
            DATA_FINA = DATA_CHART_C;
            TITLE_GRAFICO =
              "Gasto público por Categoría Presupuestal (2012-2020)";
            TITLE_GRAFICO_LEG = "CAT. PRESUPUESTAL";
            BotonesGrafico("btnCat");
            break;
          case "funcion":
            DATA_CHART_F = json;
            DATA_FINA = DATA_CHART_F;
            TITLE_GRAFICO = "Gasto público por Funciones (2012-2020)";
            TITLE_GRAFICO_LEG = "FUNCION";
            BotonesGrafico("btnFun");
            break;
          case "":
            DATA_CHART_CATEGORIA = json;
            DATA_FINA = DATA_CHART_CATEGORIA;
            TITLE_GRAFICO =
              "Gasto público de Lucha contra la violencia familiar (2012-2020)";
            TITLE_GRAFICO_LEG = "Nivel Gobierno";
          // BotonesGrafico('btnFun');
        }
        SetGrafico("T");
      });
  } else SetGrafico("T");
}

async function SetGrafico(_nb) {
  let chkPy = document.getElementById("chkChartPro");
  let chkAc = document.getElementById("chkChartAct");
  let title = document.getElementById("title-grafico");

  await new Promise((r) => setTimeout(r, 500));

  switch (_nb) {
    case "E":
      if (chkPy.checked & chkAc.checked)
        builChart(DATA_FINA.tot.nacional, TITLE_GRAFICO_LEG);
      else if (!chkPy.checked & chkAc.checked)
        builChart(DATA_FINA.act.nacional, TITLE_GRAFICO_LEG);
      else if (chkPy.checked & !chkAc.checked)
        builChart(DATA_FINA.proy.nacional, TITLE_GRAFICO_LEG);
      break;
    case "R":
      console.log("aqui");
      if (chkPy.checked & chkAc.checked)
        builChart(DATA_FINA.tot.regional, TITLE_GRAFICO_LEG);
      else if (!chkPy.checked & chkAc.checked)
        builChart(DATA_FINA.act.regional, TITLE_GRAFICO_LEG);
      else if (chkPy.checked & !chkAc.checked)
        builChart(DATA_FINA.proy.regional, TITLE_GRAFICO_LEG);
      break;
    case "M":
      if (chkPy.checked & chkAc.checked)
        builChart(DATA_FINA.tot.local, TITLE_GRAFICO_LEG);
      else if (!chkPy.checked & chkAc.checked)
        builChart(DATA_FINA.act.local, TITLE_GRAFICO_LEG);
      else if (chkPy.checked & !chkAc.checked)
        builChart(DATA_FINA.proy.local, TITLE_GRAFICO_LEG);
      break;
    case "T":
      if (chkPy.checked & chkAc.checked)
        builChart(DATA_FINA.tot.total, TITLE_GRAFICO_LEG);
      else if (!chkPy.checked & chkAc.checked)
        builChart(DATA_FINA.act.total, TITLE_GRAFICO_LEG);
      else if (chkPy.checked & !chkAc.checked)
        builChart(DATA_FINA.proy.total, TITLE_GRAFICO_LEG);
      break;
  }

  title.innerHTML = TITLE_GRAFICO;
  spinner.setAttribute("hidden", "");
}

function showSpinner() {
  spinner.className = "show";
  console.log(spinner);
  setTimeout(() => {
    spinner.className = spinner.className.replace("show", "");
  }, 5000);
}

function BotonesGrafico(e) {
  let activo = document.getElementById(e);
  let btnS = document.getElementById("btnSec");
  let btnF = document.getElementById("btnFun");
  let btnC = document.getElementById("btnCat");

  btnS.setAttribute("class", "is-centered btn-grafico small btn-inactive");
  btnF.setAttribute("class", "is-centered btn-grafico small btn-inactive");
  btnC.setAttribute("class", "is-centered btn-grafico small btn-inactive");

  activo.classList.remove("btn-inactive");
  activo.classList.add("btn-active");
}

function SWGraficoShow() {
  let btn = document.getElementById("btnShow");
  let sw = btn.getAttribute("active");

  if (sw == "0") {
    btn.setAttribute("class", "is-centered btn-grafico small btn-active");
    btn.setAttribute("active", 1);
    ReDrawChart(true);
    console.log("0");
  } else {
    btn.setAttribute("class", "is-centered btn-grafico small btn-inactive");
    btn.setAttribute("active", 0);
    ReDrawChart(false);
    console.log("1");
  }
}

function numComas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function avance(n1, n2) {
  let avance = Math.round((n2 / n1) * 100);
  return avance || 0;
}
