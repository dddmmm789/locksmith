let map;
let marker;

function initMap() {
    const jobLocation = {
        lat: parseFloat(document.getElementById('map').dataset.lat),
        lng: parseFloat(document.getElementById('map').dataset.lng)
    };

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: jobLocation
    });

    marker = new google.maps.Marker({
        position: jobLocation,
        map: map,
        title: 'Job Location'
    });
}

function startJob() {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser');
        return;
    }

    navigator.geolocation.getCurrentPosition(position => {
        const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
        };

        fetch('/api/job/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tracking_id: jobTrackingId,
                location: location
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            }
        });
    });
}

function completeJob() {
    fetch('/api/job/complete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            tracking_id: jobTrackingId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        }
    });
}

document.addEventListener('DOMContentLoaded', initMap);
