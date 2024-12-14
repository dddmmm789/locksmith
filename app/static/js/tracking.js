let map;
let locksmithMarker;
let destinationMarker;
let trackingInterval;

// Initialize the map and tracking
function initMap() {
    // Create map centered on customer's location
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: { lat: 0, lng: 0 }, // Will be updated with actual coordinates
    });

    // Create markers
    locksmithMarker = new google.maps.Marker({
        map: map,
        icon: {
            url: '/static/images/locksmith-marker.png',
            scaledSize: new google.maps.Size(40, 40)
        }
    });

    destinationMarker = new google.maps.Marker({
        map: map,
        icon: {
            url: '/static/images/destination-marker.png',
            scaledSize: new google.maps.Size(40, 40)
        }
    });

    // Start tracking
    startTracking();
}

function startTracking() {
    // Update location every 30 seconds
    trackingInterval = setInterval(updateLocation, 30000);
    updateLocation(); // Initial update
}

async function updateLocation() {
    try {
        const response = await fetch(`/api/location/${trackingId}`);
        const data = await response.json();
        
        if (data.locksmith_location) {
            const locksmithPos = {
                lat: data.locksmith_location.lat,
                lng: data.locksmith_location.lng
            };
            
            // Update locksmith marker
            locksmithMarker.setPosition(locksmithPos);
            
            // Update destination marker if needed
            if (data.destination) {
                destinationMarker.setPosition({
                    lat: data.destination.lat,
                    lng: data.destination.lng
                });
            }
            
            // Update ETA
            document.getElementById('eta').textContent = data.eta || 'Calculating...';
            
            // Center map to show both markers
            const bounds = new google.maps.LatLngBounds();
            bounds.extend(locksmithMarker.getPosition());
            bounds.extend(destinationMarker.getPosition());
            map.fitBounds(bounds);
        }
    } catch (error) {
        console.error('Error updating location:', error);
    }
}

function correctAddress() {
    const newAddress = prompt('Please enter the correct address:');
    if (newAddress) {
        fetch('/api/update-address', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tracking_id: trackingId,
                address: newAddress
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Address updated successfully!');
                location.reload();
            } else {
                alert('Failed to update address. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }
}

// Initialize map when page loads
window.addEventListener('load', initMap);

// Cleanup when page is closed
window.addEventListener('beforeunload', () => {
    if (trackingInterval) {
        clearInterval(trackingInterval);
    }
}); 