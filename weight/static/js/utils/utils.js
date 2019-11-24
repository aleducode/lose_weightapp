const utilsPayment = {
  /* Method to validate a promotional code for companies and get the price
   * @param code Promotional code to validate
   * @param url url endpoint to validate
   * @param csrf_token security token
   */

  checkCode: (code, url, csrf_token) => {
    return new Promise((resolve, reject) => {
      let result;
      if (code) {
        if (code && code.replace(/^\s+|\s+$/g, "").length != 0) {
          $.ajax({
            type: "POST",
            url: url,
            data: {
              code: code,
              csrfmiddlewaretoken: csrf_token
            },
            dataType: "json"
          })
            .done(function(response) {
              result = parseFloat(response.membership, 10)
                .toFixed(2)
                .replace(/(\d)(?=(\d{3})+\.)/g, "$1,")
                .toString();
              resolve(result);
            })
            .fail(function(error, exception) {
              let msg_err = "";
              if (error.status === 0) {
                msg_err = "Not connect. Verify Network.";
              } else if (error.status == 404) {
                msg_err = "Código no encontrado.";
              } else if (error.status == 500) {
                msg_err = "Error interno.";
              } else if (exception === "parsererror") {
                msg_err = "Requested JSON parse failed.";
              } else if (exception === "timeout") {
                msg_err = "Time out error.";
              } else if (exception === "abort") {
                msg_err = "Ajax request aborted.";
              } else {
                msg_err = "Error inesperado. " + error.responseText;
              }
              if (msg_err) {
                result = msg_err;
                reject(result);
              }
            });
        }
      }
    });
  },

  hideCode: () => {
    $("#id_code").val("");
    $("#id_code").removeClass("is-valid");
    $("#id_code").removeClass("is-invalid");
    $("#id_code").toggle();
  }
};


const utilsButton = {
  loader: (element) => {
    $(element).prop("disabled",true);
    $(element).html("<span class='spinner-grow spinner-grow-sm'></span>")
  }
}
