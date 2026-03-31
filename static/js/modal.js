var flagModalShare = false;

function verModalShare(evt) {
    let modal = document.getElementById('modal_share');
    if (flagModalShare) {

        modal.style.display = "none";
        flagModalShare = false;

        // let ulrImage = 'http://localhost:5000/static/images/icons/salida/share.png';
        // evt.setAttribute('src', ulrImage);
    } else {
        //   verificarModalAbiertosSalida();
        let btn = document.getElementById('btnShare');
        flagModalShare = true;
        modal.style.display = "block";

        // let ulrImage = 'http://localhost:5000/static/images/icons/salida/f_share.png';
        // evt.setAttribute('src', ulrImage);
    }
}