const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function diagnoseImage({ file, latitude, longitude, radiusKm = 10 }) {
	const formData = new FormData();
	formData.append('image', file, file.name);

	if (latitude !== '' && latitude !== null && latitude !== undefined) {
		formData.append('latitude', String(latitude));
	}
	if (longitude !== '' && longitude !== null && longitude !== undefined) {
		formData.append('longitude', String(longitude));
	}
	if (radiusKm !== '' && radiusKm !== null && radiusKm !== undefined) {
		formData.append('radius_km', String(radiusKm));
	}

	const response = await fetch(`${API_BASE_URL}/vision/diagnose`, {
		method: 'POST',
		body: formData,
	});
	const payload = await response.json().catch(() => ({}));

	if (!response.ok) {
		throw new Error(payload.detail || 'Diagnosis request failed.');
	}

	return payload;
}
