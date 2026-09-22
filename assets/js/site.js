/* ==========================================================================
   Comlynk — landing page

   Ce fichier ne fait que deux choses :
   1. activer les boutons « App Store » le jour de la publication ;
   2. mémoriser la langue choisie pour la redirection de la racine.
   ========================================================================== */

(function () {
  "use strict";

  /* ------------------------------------------------------------------------
     1. Lien App Store

     👉 LE JOUR DU LANCEMENT : colle l'URL de la fiche App Store ci-dessous.
        C'est la seule ligne à modifier dans tout le site — les deux boutons
        (héro et appel final), dans les deux langues, deviennent cliquables.

        Exemple : "https://apps.apple.com/app/id1234567890"
     ------------------------------------------------------------------------ */

  var APP_STORE_URL = "";

  if (APP_STORE_URL) {
    document.querySelectorAll("[data-store]").forEach(function (button) {
      var link = document.createElement("a");
      link.className = button.className;
      link.href = APP_STORE_URL;
      link.rel = "noopener";
      link.innerHTML = button.innerHTML;
      button.replaceWith(link);
    });

    document.querySelectorAll("[data-store-soon]").forEach(function (note) {
      note.remove();
    });
  }

  /* ------------------------------------------------------------------------
     2. Mémorisation de la langue

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
