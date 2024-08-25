// this is the custom code to fulfill our requirement

// ///////////////////////////////////////////////////////

let autocomplete;

function initAutoComplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById("id_address"),
    {
      // geocode is address whiles establishement will be used for office or restaurant addresses
      types: ["geocode", "establishment"],
      //default in this app is "CA"
      componentRestrictions: { country: ["ca"] },
    }
  );
  // function to specify what should happen when the prediction is clicked
  autocomplete.addListener("place_changed", onPlaceChanged);
}

function onPlaceChanged() {
  var place = autocomplete.getPlace();

  // User did not select the prediction. Reset the input field or alert()
  if (!place.geometry) {
    document.getElementById("id_address").placeholder = "Start typing...";
  } else {
    console.log("place name=>", place.name);
  }
  // get the address components and assign them to the fields
  //   console.log(place)
  var geocoder = new google.maps.Geocoder();

  var address = document.getElementById("id_address").value;

  geocoder.geocode({ address: address }, function (results, status) {
    // console.log('results=>', results)
    // console.log('status=>', status)
    if (status == google.maps.GeocoderStatus.OK) {
      // get the latitude and longitude
      var latitude = results[0].geometry.location.lat();
      var longitude = results[0].geometry.location.lng();

      // console.log('lat=>', latitude)
      // console.log('lng=>', longitude)

      // using jquery automatically put the value of var latitude into the field of the id id_latitude(that is the id of the latitude field)
      $("#id_latitude").val(latitude);
      $("#id_longitude").val(longitude);

      $("#id_address").val(address);
      console.log(address);
    }
  });
  // loop through the address components and assign other address components to their respective fields
  console.log(place.address_components);
  for (var i = 0; i < place.address_components.length; i++) {
    for (var j = 0; j < place.address_components[i].types.length; j++) {
      // get country and place it auto into the country field
      if (place.address_components[i].types[j] == "country") {
        $("#id_country").val(place.address_components[i].long_name);
      }
      // get province

      if (
        place.address_components[i].types[j] == "administrative_area_level_1"
      ) {
        $("#id_province").val(place.address_components[i].long_name);
      }

      // get city

      if (place.address_components[i].types[j] == "locality") {
        $("#id_city").val(place.address_components[i].long_name);
      }

      // get postal code

      if (place.address_components[i].types[j] == "postal_code") {
        $("#id_postal_code").val(place.address_components[i].long_name);
      } else {
        // if the address has no postal code make the field blank
        $("#id_postal_code").val("");
      }
    }
  }
}

// ---------------------------------------------------------------------------------------------

// $(document).ready(function () {
//   $(".add_to_cart").on("click", function (e) {
//     e.preventDefault();
//     alert("testing123");
//   });
// });

// this function will be called when either the increase or decrese cart item button is clicked
// to use this ajax request funct add the jquery script cdn to head part of the base.html
jQuery(document).ready(function () {
  jQuery(".add_to_cart").on("click", function (e) {
    e.preventDefault();
    // get the food id when the button is clicked in the add or remove itme from cart
    food_id = $(this).attr("data-id");
    // get the url when the button is clicked in the add or remove itme from cart
    url = $(this).attr("data-url");

    data = {
      food_id: food_id,
    };
    // send the food_id to the add_to_cart view using ajax request
    $.ajax({
      type: "GET",
      url: url,
      data: data,
      success: function (response) {
        console.log(response);
        if (response.status == "login_required") {
          swal(response.message, "", "info").then(function () {
            window.location = "/accounts/login";
          });
        } else if (response.status == "Failure") {
          swal(response.message, "", "error");
        } else {
          $("#cart_counter").html(response.cart_counter["cart_count"]);
          $("#qty-" + food_id).html(response.qty);

          // call the get_cart_amount function here. NB: this function is in the marketplace/context_processors.py
          // this part is responsible for updating the cart amounts on the frontpage
          applyCartAmounts(
            response.get_cart_amount["subtotal"],
            response.get_cart_amount["tax_dict"],
            response.get_cart_amount["grand_total"]
          );
        }
      },
    });
  });

  // remove food from cart
  jQuery(".remove_from_cart").on("click", function (e) {
    e.preventDefault();
    // get the food id when the button is clicked in the add or remove itme from cart
    food_id = $(this).attr("data-id");
    // get the url when the button is clicked in the add or remove itme from cart
    url = $(this).attr("data-url");
    // i added this so that i will be able to remove the cart item li fro
    // from the cart page when the item quantity is less than 1 or = 0
    // remember to add the id={{item.id}} in the element with the class=remove_cart_item which is inside the
    // cart_page.html file
    cart_id = $(this).attr("id");

    data = {
      food_id: food_id,
    };
    // send the food_id to the add_to_cart view using ajax request
    $.ajax({
      type: "GET",
      url: url,
      data: data,
      success: function (response) {
        // this logs the response in the console when you inspect
        console.log(response);
        // check if the response in the remove_from_cart view is login_required for ia_authenticated
        if (response.status == "login_required") {
          // using the sweet alert display the message in the jsonresponse which is in the view
          // NB: to use the sweet aler make sure to add the cdn script in the head
          // part of the base.htm. https://sweetalert.js.org/guides/
          swal(response.message, "", "info").then(function () {
            // redirect the user to the login page
            window.location = "/accounts/login";
          });
        } else if (response.status == "Failure") {
          swal(response.message, "", "error");
        } else {
          // get the id of the elemnt with the badge and put the response on it. The badge is on the navbar. here I am
          // picking only the cart_count from the cart_counter which will be in the jsonresponse not all the response
          $("#cart_counter").html(response.cart_counter["cart_count"]);
          // get the id of the elemnt with the quantity qty-food_id and put the response on it.
          // picking only the quantity from the jsonresponse not all the response
          $("#qty-" + food_id).html(response.qty);

          // call the get_cart_amount function here. NB: this function is in then marketplace/context_processors.py
          applyCartAmounts(
            response.get_cart_amount["subtotal"],
            response.get_cart_amount["tax_dict"],
            response.get_cart_amount["grand_total"]
          );

          // run the two functions only if the user is in the cart page
          if (window.location.pathname == "/marketplace/cart_page/") {
            // this will remove the li of the cart_item whose quantity is 0
            removeCartItem(response.qty, cart_id);
            // this will show the cart is empty f there is no item in the cart
            checkEmptyCart();
          }
        }
      },
    });
  });

  // place the cart item quantity in between the add and decrease quantity buttons on load
  // get the element whose class is item_qty. This item_qty is in the vendor_details.html
  $(".item_qty").each(function () {
    // get the value of the id of that element
    var the_id = $(this).attr("id");
    // get the value of the data-qty of that element
    var qty = $(this).attr("data-qty");
    // assign the qty to the html value of the element
    $("#" + the_id).html(qty);
  });

  // delete cart item

  jQuery(".delete_cart_item").on("click", function (e) {
    e.preventDefault();
    // get the food id when the button is clicked in the add or remove itme from cart
    cart_id = $(this).attr("data-id");
    // get the url when the button is clicked in the add or remove itme from cart
    url = $(this).attr("data-url");

    data = {
      cart_id: cart_id,
    };

    // send the food_id to the add_to_cart view using ajax request
    $.ajax({
      type: "GET",
      url: url,
      data: data,
      success: function (response) {
        console.log(response);
        if (response.status == "Failure") {
          swal(response.message, "", "error");
        } else {
          $("#cart_counter").html(response.cart_counter["cart_count"]);
          swal(response.status, response.message, "success");

          // call the get_cart_amount function here. NB: this function is in then marketplace/context_processors.py
          applyCartAmounts(
            response.get_cart_amount["subtotal"],
            response.get_cart_amount["tax_dict"],
            response.get_cart_amount["grand_total"]
          );

          // run the two functions only is the user is in the cart page

          if (window.location.pathname == "/marketplace/cart_page/") {
            // calling the remove CartItem function. pass 0 and cart_id as arguments
            removeCartItem(0, cart_id);
            // check if the cart is empty and show the Cart is empty
            checkEmptyCart();
          }
        }
      },
    });
  });

  // delete the cart element if the quantity is zero
  // this will remove the cart item from the cart page without reloading the page
  function removeCartItem(cartItemQty, cart_id) {
    // run this code if the user is in the cart_page.html

    // check if the cart item quantity is zero for that particular item
    if (cartItemQty <= 0) {
      // get the elemnt with the particular id in the html pages and remove it
      // NB: this function will be called when the delete_cart_function above is executed.
      // refer in the delete_cart_item item function above
      //remove cart item
      document.getElementById("cart-item-" + cart_id).remove();
    }
  }

  // Check cart counter if it is zero and show the Your counter is empty

  function checkEmptyCart() {
    // Get the innerHTML of the cart_counter element and trim any extra spaces
    var cartCounterElement = document.getElementById("cart_counter");

    if (cartCounterElement) {
      var cart_counter = cartCounterElement.innerHTML.trim();

      // Convert the string to a number for comparison
      var cartCount = parseInt(cart_counter, 10);

      // Check if cartCount is a valid number and if it is zero
      if (!isNaN(cartCount) && cartCount === 0) {
        var emptyCartElement = document.getElementById("empty-cart");

        if (emptyCartElement) {
          emptyCartElement.style.display = "block";
        }
      }
    }
  }

  // Check if the cart is empty
  // function checkEmptyCart() {
  //   var cart_counter = document.getElementById("cart_counter").innerHTML;
  //   if (cart_counter == 0) {
  //     document.getElementById("empty-cart").style.display = "block";
  //   }
  // }

  // apply cart amounts

  function applyCartAmounts(subtotal, tax_dict, grand_total) {
    // get the elements of subtotal, tax and total from the cart_page using their ids
    // and assign the total, tax and subtotal to their html values. After writing this function call it in the add_to_cart, remove_from_cart and delete_cart
    // functions above respectively
    if (window.location.pathname == "/marketplace/cart_page/") {
      $("#subtotal").html(subtotal);
      // $("#tax").html(tax);
      $("#total").html(grand_total);
      // key1 is the taxtype, key2 is the tax percent
      for (key1 in tax_dict) {
        for (key2 in tax_dict[key1]) {
          // Escape the key1 to handle special characters like '/', etc.
          // let taxElementId = $.escapeSelector("tax-" + key1);
          $("#tax-" + key1).html(tax_dict[key1][key2]);
        }
      }
    }
  }
  // add opening hours

  $(".add_hours").on("click", function (e) {
    e.preventDefault();
    var day = document.getElementById("id_day").value;
    var from_hour = document.getElementById("id_from_hour").value;
    var to_hour = document.getElementById("id_to_hour").value;
    var is_closed = document.getElementById("id_is_closed").checked;
    // get the value of the csrf token using jquery. I use .val because it is jquery
    var csrf_token = $("input[name=csrfmiddlewaretoken]").val();
    url = document.getElementById("add_hour_url").value;

    // console.log(day, from_hour,to_hour,is_closed, csrf_token)
    // check if all the fields are filled

    // if is closed is checked
    if (is_closed) {
      // then is closed is true
      is_closed = true;
      // save if day is selected
      condition = "day !=''";
    } else {
      // otherwise is closed is false
      is_closed = false;
      // save if day is slected and from hour is selected and to hour is selected
      condition = "day != '' && from_hour != '' && to_hour != ''";
    }
    // use the above condition. I am using eval because the condition contains strings
    // check the above conditions if you have to save save or do the opposite
    if (eval(condition)) {
      // send the ajax request to the add_opening_hours view
      $.ajax({
        type: "POST",
        url: url,
        // pass the data you want to send to the view thats to the url
        data: {
          day: day,
          from_hour: from_hour,
          to_hour: to_hour,
          is_closed: is_closed,
          csrfmiddlewaretoken: csrf_token,
        },
        // when successfully sent the ajax request, receive the response. This response will be
        // the jsonresponse that will be returned by the add_opening_hours view
        // go to the add_opening_hours view to set the json response
        success: function (response) {
          // console.log(response)
          if (response.status == "success") {
            // the entire html block that displays the day, hours was copied from the opening_hours.html file and assigned to html
            // check if closed is slected
            if (response.is_closed == "closed") {
              html =
                "<tr id='hour-" +
                response.id +
                "'><td><b>" +
                response.day +
                '</b></td><td>Closed</td><td><a href="" class="remove_hour" data-url="/vendors/remove_opening_hours/' +
                response.id +
                '/">Remove</a></td></tr>';
            } else {
              // and make the neccessary changes by passing the response
              html =
                "<tr id='hour-" +
                response.id +
                "'><td><b>" +
                response.day +
                "</b></td><td>" +
                response.from_hour +
                " - " +
                response.to_hour +
                '</td><td><a href="" class="remove_hour" data-url="/vendors/remove_opening_hours/' +
                response.id +
                '/">Remove</a></td></tr>';
            }

            // add the html to the already existing table using the tables class
            $(".opening-hours").append(html);
            // reset the form using the forms id
            document.getElementById("opening-hours").reset();
          } else {
            // show error message using sweet alert
            swal(response.message, "", "info");
          }
        },
      });
    } else {
      // console.log('please fill all')
      swal("Please Fill all the fields", "", "info");
    }
  });

  //-------------------------------------------------------------------------------

  //Remove opening hours
  // $('.remove_hour').on('click', function(e){
  //   e.preventDefault()
  //   url = $(this).attr('data-url')
  //   $.ajax({
  //     type:'GET',
  //     url:url,
  //     success: function(response){

  //       if (response.status =='success'){
  //         // document.getElementById('id').remove()
  //         // get the tr id and remove the tr. this will remove entire row
  //         document.getElementById('hour-'+response.id).remove()
  //       }
  //     }
  //   })
  // })

  $(document).on("click", ".remove_hour", function (e) {
    e.preventDefault();

    url = $(this).attr("data-url");
    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        if (response.status == "success") {
          // document.getElementById('id').remove()
          // get the tr id and remove the tr. this will remove entire row
          document.getElementById("hour-" + response.id).remove();
        }
      },
    });
  });

  // document ready closed
});

// Wnen the add_to_cart button is clicked it will take the respective food_id and url
// then it will send the request to the view using the ajax. This will get the Httpresponse
//from the add_to_cart view. That is the response received in the success function
// --------------------------------------------------------------------------------------
