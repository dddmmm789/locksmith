class JobTracker {
    constructor(jobId) {
        this.jobId = jobId;
        this.map = null;
        this.marker = null;
        this.updateInterval = 30000; // 30 seconds
    }

    async init() {
        await this.initMap();
        this.startTracking();
    }

    async initMap() {
        const response = await fetch(`/api/job/${this.jobId}/location`);
        const data = await response.json();
        
        this.map = new google.maps.Map(document.getElementById('map'), {
            zoom: 15,
            center: { lat: data.latitude, lng: data.longitude }
        });
        
        this.marker = new google.maps.Marker({
            position: { lat: data.latitude, lng: data.longitude },
            map: this.map,
            title: 'Service Location'
        });
    }

    startTracking() {
        setInterval(() => this.updateLocation(), this.updateInterval);
    }

    async updateLocation() {
        const response = await fetch(`/api/job/${this.jobId}/location`);
        const data = await response.json();
        
        const position = new google.maps.LatLng(data.latitude, data.longitude);
        this.marker.setPosition(position);
        this.map.panTo(position);
    }
}
