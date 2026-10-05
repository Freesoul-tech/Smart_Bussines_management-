document.addEventListener("DOMContentLoaded", function () {

    const modelCards = document.querySelectorAll(".model-card");
    const modelField = document.getElementById("id_business_model");
    const continueButton = document.getElementById("continueButton");

    const form = document.getElementById("businessSetupForm");

    const certificateInput =
        document.getElementById("id_certificate");

    const fileName =
        document.getElementById("fileName");


    /*
    =========================================================
    BUSINESS MODEL SELECTION
    =========================================================
    */

    modelCards.forEach(function (card) {

        card.addEventListener("click", function () {

            modelCards.forEach(function (item) {
                item.classList.remove("active");
            });

            card.classList.add("active");

            const selectedModel = card.dataset.model;

            if (modelField) {
                modelField.value = selectedModel;
            }

            if (continueButton) {
                continueButton.disabled = false;
            }

        });

    });


    /*
    =========================================================
    CERTIFICATE FILE
    =========================================================
    */

    if (certificateInput && fileName) {

        certificateInput.addEventListener("change", function () {

            if (this.files.length > 0) {
                fileName.textContent = this.files[0].name;
            } else {
                fileName.textContent = "Choose certificate";
            }

        });

    }


    /*
    =========================================================
    BUSINESS LOCATION
    =========================================================
    */

    const locationInput =
        document.getElementById("id_location");

    const locateBusinessButton =
        document.getElementById("locateBusinessButton");

    const mapElement =
        document.getElementById("businessLocationMap");

    const locationStatus =
        document.getElementById("locationStatus");

    const clearLocationButton =
        document.getElementById("clearLocationButton");


    let locationMap = null;
    let locationMarker = null;

    let searchTimer = null;
    let suggestionBox = null;


   /*
    =========================================================
    DEFAULT MAP LOCATION
    Malawi / Lilongwe
    =========================================================
    */

    const defaultLatitude = -13.9626;
    const defaultLongitude = 33.7741;
    const defaultZoom = 6;


    /*
    =========================================================
    CREATE SUGGESTION BOX
    =========================================================
    */

    function createSuggestionBox() {

        if (!locationInput) {
            return null;
        }

        if (suggestionBox) {
            return suggestionBox;
        }


        suggestionBox =
            document.createElement("div");

        suggestionBox.className =
            "location-suggestions";


        locationInput.parentElement.style.position =
            "relative";


        locationInput.parentElement.appendChild(
            suggestionBox
        );


        return suggestionBox;

    }


    /*
    =========================================================
    SHOW SUGGESTIONS
    =========================================================
    */

    function showSuggestions(results) {

        const box =
            createSuggestionBox();

        if (!box) {
            return;
        }


        box.innerHTML = "";


        if (!results || results.length === 0) {

            box.style.display = "none";

            return;
        }


        results.forEach(function (result) {

            const item =
                document.createElement("button");

            item.type = "button";

            item.className =
                "location-suggestion-item";


            /*
            Main name
            */

            const title =
                document.createElement("strong");

            title.textContent =
                result.name ||
                result.display_name.split(",")[0];


            /*
            Full address
            */

            const address =
                document.createElement("span");

            address.textContent =
                result.display_name;


            item.appendChild(title);
            item.appendChild(address);


            /*
            -------------------------------------------------
            SELECT SUGGESTION
            -------------------------------------------------
            */

            item.addEventListener(
                "click",
                function () {

                    const latitude =
                        parseFloat(result.lat);

                    const longitude =
                        parseFloat(result.lon);


                    /*
                    Fill the Django location field
                    */

                    if (locationInput) {

                        locationInput.value =
                            result.display_name;

                    }


                    /*
                    Hide suggestions
                    */

                    box.style.display =
                        "none";


                    /* Pin the selected address immediately. */

                    setLocation(latitude, longitude);

                }
            );


            box.appendChild(item);

        });


        box.style.display =
            "block";

    }


    /*
    =========================================================
    SEARCH LOCATION
    =========================================================
    */

    function searchLocation(query) {

        if (!query || query.trim().length < 2) {

            if (suggestionBox) {
                suggestionBox.style.display = "none";
            }

            return;
        }


        fetch(
            "https://nominatim.openstreetmap.org/search?format=jsonv2&addressdetails=1&limit=5&q=" +
            encodeURIComponent(query.trim())
        )
        .then(function (response) {

            if (!response.ok) {
                throw new Error("Location search failed.");
            }

            return response.json();

        })
        .then(function (results) {

            showSuggestions(results);

        })
        .catch(function () {

            if (suggestionBox) {

                suggestionBox.style.display =
                    "none";

            }

        });

    }


    /*
    =========================================================
    LOCATION INPUT AUTOCOMPLETE
    =========================================================
    */

    if (locationInput) {

        locationInput.addEventListener(
            "input",
            function () {

                const query =
                    this.value.trim();


                clearTimeout(
                    searchTimer
                );


                searchTimer =
                    setTimeout(
                        function () {

                            searchLocation(
                                query
                            );

                        },
                        500
                    );

            }
        );


        /*
        -----------------------------------------------------
        FOCUS
        -----------------------------------------------------
        */

        locationInput.addEventListener(
            "focus",
            function () {

                if (
                    this.value.trim().length >= 2
                ) {

                    searchLocation(
                        this.value.trim()
                    );

                }

            }
        );

    }


    /*
    =========================================================
    CLOSE SUGGESTIONS WHEN CLICKING OUTSIDE
    =========================================================
    */

    document.addEventListener(
        "click",
        function (event) {

            if (
                suggestionBox &&
                locationInput &&
                !locationInput.contains(event.target) &&
                !suggestionBox.contains(event.target)
            ) {

                suggestionBox.style.display =
                    "none";

            }

        }
    );


    /*
    =========================================================
    INITIALIZE MAP
    =========================================================
    */

    function initializeMap() {

        if (
            !mapElement ||
            typeof L === "undefined"
        ) {

            return;

        }


        if (locationMap) {
            return;
        }


        locationMap =
            L.map(
                mapElement,
                {
                    zoomControl: true
                }
            )
            .setView(
                [
                    defaultLatitude,
                    defaultLongitude
                ],
                defaultZoom
            );


        /*
        -----------------------------------------------------
        ESRI BASEMAP
        -----------------------------------------------------
        */

        L.tileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            {
                maxZoom: 19,

                attribution:
                    "Tiles &copy; Esri"
            }
        )
        .addTo(locationMap);


        /*
        -----------------------------------------------------
        CLICK MAP
        -----------------------------------------------------
        */

        locationMap.on(
            "click",
            function (event) {

                setLocation(
                    event.latlng.lat,
                    event.latlng.lng
                );

            }
        );


        locationMap.on(
            "dragend",
            function () {

                const center =
                    locationMap.getCenter();


                setLocation(
                    center.lat,
                    center.lng,
                    false
                );

            }
        );


        setTimeout(
            function () {

                locationMap.invalidateSize();

            },
            150
        );

    }


    /*
    =========================================================
    OPEN MAP
    =========================================================
    */

    function openMap() {

        if (!mapElement) {
            return;
        }


        initializeMap();


        mapElement.classList.add(
            "map-visible"
        );


        setTimeout(
            function () {

                if (locationMap) {

                    locationMap.invalidateSize();

                }

            },
            200
        );

    }


    /*
    =========================================================
    SET LOCATION
    =========================================================
    */

    function setLocation(
        latitude,
        longitude,
        centerMap = true
    ) {

        initializeMap();


        if (!locationMap) {
            return;
        }


        const coordinates = [
            latitude,
            longitude
        ];


        if (locationMarker) {

            locationMarker.setLatLng(coordinates);

        } else {

            locationMarker = L.marker(coordinates)
                .addTo(locationMap);

        }


        /*
        -----------------------------------------------------
        MOVE MAP
        -----------------------------------------------------
        */

        if (centerMap) {

            locationMap.setView(
                coordinates,
                17
            );

        }


        if (locationInput) {

            locationInput.value =
                latitude.toFixed(6) +
                ", " +
                longitude.toFixed(6);

        }


        /*
        -----------------------------------------------------
        GET LOCATION NAME
        -----------------------------------------------------
        */

        if (locationStatus) {

            locationStatus.textContent =
                "Getting location name...";

        }


        fetch(
            "https://nominatim.openstreetmap.org/reverse?format=jsonv2&addressdetails=1&lat=" +
            encodeURIComponent(latitude) +
            "&lon=" +
            encodeURIComponent(longitude)
        )
        .then(function (response) {

            if (!response.ok) {

                throw new Error(
                    "Reverse geocoding failed."
                );

            }

            return response.json();

        })
        .then(function (data) {

            let locationName = "";


            if (
                data &&
                data.display_name
            ) {

                locationName =
                    data.display_name;

            }


            /*
            Fill the form automatically
            */

            if (locationInput) {

                locationInput.value =
                    locationName ||
                    latitude.toFixed(6) +
                    ", " +
                    longitude.toFixed(6);

            }


            if (locationStatus) {

                locationStatus.textContent =
                    "Location pinned successfully.";

            }

        })
        .catch(function () {

            /*
            Even if address lookup fails,
            keep the coordinates.
            */

            if (locationInput) {

                locationInput.value =
                    latitude.toFixed(6) +
                    ", " +
                    longitude.toFixed(6);

            }


            if (locationStatus) {

                locationStatus.textContent =
                    "Location pinned. Coordinates saved.";

            }

        });


    }


    /*
    =========================================================
    DEVICE CURRENT LOCATION
    =========================================================
    */

    function useDeviceLocation() {

        if (!navigator.geolocation) {

            if (locationStatus) {

                locationStatus.textContent =
                    "Your device does not provide location services.";

            }

            openMap();

            return;
        }


        if (locationStatus) {

            locationStatus.textContent =
                "Requesting your current location...";

        }


        navigator.geolocation.getCurrentPosition(

            function (position) {

                const latitude =
                    position.coords.latitude;

                const longitude =
                    position.coords.longitude;


                /*
                Open the floating map
                */

                openMap();


                /*
                Show the real device location
                */

                setLocation(
                    latitude,
                    longitude
                );

            },


            function (error) {

                let message =
                    "Unable to access your current location.";


                if (
                    error.code ===
                    error.PERMISSION_DENIED
                ) {

                    message =
                        "Location permission was denied. You can search for your location or pin it manually on the map.";

                }
                else if (
                    error.code ===
                    error.POSITION_UNAVAILABLE
                ) {

                    message =
                        "Your device location is currently unavailable. You can search or pin the location manually.";

                }
                else if (
                    error.code ===
                    error.TIMEOUT
                ) {

                    message =
                        "Finding your location took too long. You can search or pin the location manually.";

                }


                if (locationStatus) {

                    locationStatus.textContent =
                        message;

                }


                /*
                Still open the map
                */

                openMap();

            },


            {
                enableHighAccuracy: true,

                timeout: 15000,

                maximumAge: 0

            }

        );

    }


    /*
    =========================================================
    LOCATION BUTTON
    =========================================================
    */

    if (locateBusinessButton) {

        locateBusinessButton.addEventListener(
            "click",
            function () {

                /*
                First attempt:
                use the real device location.
                */

                useDeviceLocation();

            }
        );

    }


    /*
    =========================================================
    CLEAR LOCATION
    =========================================================
    */

    if (clearLocationButton) {

        clearLocationButton.addEventListener(
            "click",
            function () {

                if (locationInput) {

                    locationInput.value = "";

                }


                if (
                    locationMarker &&
                    locationMap
                ) {

                    locationMap.removeLayer(
                        locationMarker
                    );

                    locationMarker = null;

                }


                if (locationMap) {

                    locationMap.setView(
                        [
                            defaultLatitude,
                            defaultLongitude
                        ],
                        defaultZoom
                    );

                }


                if (mapElement) {

                    mapElement.classList.remove(
                        "map-visible"
                    );

                }


                if (suggestionBox) {

                    suggestionBox.style.display =
                        "none";

                }


                if (locationStatus) {

                    locationStatus.textContent =
                        "Location is optional. You can enter it manually or pin it on the map.";

                }

            }
        );

    }


    /*
    =========================================================
    FORM VALIDATION
    =========================================================
    */

    if (form) {

        form.addEventListener(
            "submit",
            function (event) {

                if (
                    !modelField ||
                    !modelField.value
                ) {

                    event.preventDefault();

                    alert(
                        "Select a business model before continuing."
                    );

                }

            }
        );

    }


    initializeMap();

});
