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
      console.log(address)
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
