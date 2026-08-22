import { useEffect, useState } from 'react';
import { diagnoseImage } from '../api/client';

function ResourceList({ resources }) {
	if (!resources?.length) return null;

	return (
		<section>
			<h3>Learn more</h3>
			<ul>
				{resources.map((resource) => (
					<li key={resource.url}>
						<a href={resource.url} target="_blank" rel="noreferrer">
							{resource.title}
						</a>{' '}
						<span>({resource.language})</span>
					</li>
				))}
			</ul>
		</section>
	);
}

export default function ImageUpload({ onResult }) {
	const [file, setFile] = useState(null);
	const [previewUrl, setPreviewUrl] = useState('');
	const [latitude, setLatitude] = useState('');
	const [longitude, setLongitude] = useState('');
	const [radiusKm, setRadiusKm] = useState('10');
	const [result, setResult] = useState(null);
	const [error, setError] = useState('');
	const [isLoading, setIsLoading] = useState(false);

	useEffect(() => () => previewUrl && URL.revokeObjectURL(previewUrl), [previewUrl]);

	const handleFileChange = (event) => {
		const selectedFile = event.target.files?.[0] || null;
		setFile(selectedFile);
		setResult(null);
		setError('');
		setPreviewUrl(selectedFile ? URL.createObjectURL(selectedFile) : '');
	};

	const handleSubmit = async (event) => {
		event.preventDefault();
		if (!file) {
			setError('Choose an image first.');
			return;
		}

		setIsLoading(true);
		setError('');
		try {
			const diagnosis = await diagnoseImage({ file, latitude, longitude, radiusKm });
			setResult(diagnosis);
			onResult?.(diagnosis);
		} catch (requestError) {
			setError(requestError.message || 'Diagnosis request failed.');
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<main>
			<h1>Plant diagnosis</h1>
			<form onSubmit={handleSubmit}>
				<label>
					Leaf image
					<input type="file" accept="image/*" onChange={handleFileChange} />
				</label>
				{previewUrl && <img src={previewUrl} alt="Selected leaf" width="320" />}

				<fieldset>
					<legend>Optional location</legend>
					<label>
						Latitude
						<input value={latitude} onChange={(event) => setLatitude(event.target.value)} inputMode="decimal" />
					</label>
					<label>
						Longitude
						<input value={longitude} onChange={(event) => setLongitude(event.target.value)} inputMode="decimal" />
					</label>
					<label>
						Radius (km)
						<input value={radiusKm} onChange={(event) => setRadiusKm(event.target.value)} type="number" min="1" step="1" />
					</label>
				</fieldset>

				<button type="submit" disabled={isLoading}>
					{isLoading ? 'Analyzing...' : 'Analyze image'}
				</button>
			</form>

			{error && <p role="alert">{error}</p>}
			{result && (
				<article>
					<h2>{result.condition || result.status}</h2>
					<p>Status: {result.status}</p>
					<p>Confidence: {typeof result.confidence === 'number' ? `${(result.confidence * 100).toFixed(1)}%` : 'Unavailable'}</p>
					{result.message && <p>{result.message}</p>}
					{result.what_to_do_now?.length > 0 && <section><h3>What to do now</h3><ul>{result.what_to_do_now.map((item) => <li key={item}>{item}</li>)}</ul></section>}
					{result.prevention?.length > 0 && <section><h3>Prevention</h3><ul>{result.prevention.map((item) => <li key={item}>{item}</li>)}</ul></section>}
					{result.recommended_inputs?.length > 0 && <section><h3>Recommended inputs</h3><ul>{result.recommended_inputs.map((item) => <li key={item.category}>{item.category}: {item.purpose}</li>)}</ul></section>}
					{result.nearby_sellers?.length > 0 && <section><h3>Nearby sellers</h3><ul>{result.nearby_sellers.map((seller) => <li key={`${seller.name}-${seller.maps_uri}`}><a href={seller.maps_uri} target="_blank" rel="noreferrer">{seller.name}</a> ({seller.distance_km} km) - stock not verified</li>)}</ul></section>}
					<ResourceList resources={result.learning_resources} />
				</article>
			)}
		</main>
	);
}
