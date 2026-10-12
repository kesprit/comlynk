/* ==========================================================================
   Comlynk — landing page

   Ce fichier ne fait qu'une chose : mémoriser la langue choisie pour la
   redirection de la racine.
   ========================================================================== */

(function () {
  "use strict";

  /* ------------------------------------------------------------------------
     Mémorisation de la langue

     La racine du site (index.html) lit cette valeur pour renvoyer le visiteur
     vers la langue qu'il a choisie la dernière fois, plutôt que de se fier
     uniquement à la langue du navigateur.
     ------------------------------------------------------------------------ */

  var lang = document.documentElement.lang;

  if (lang) {
    try {
      window.localStorage.setItem("comlynk-lang", lang.slice(0, 2));
    } catch (error) {
      /* Navigation privée ou stockage bloqué : sans importance. */
    }
  }
})();
