async function CopyPriceChange() {
    try {
        // Fetch text from the backend API
        const response = await fetch('/get-copy-price-change');
        const data = await response.json();
        const textToCopy = data.text;
        
        // Copy the text to clipboard
        navigator.clipboard.writeText(textToCopy).then(() => {
            alert('Text copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    } catch (error) {
        console.error('Error fetching text: ', error);
    }
}

async function CopyInjuryUpdates(id) {
    try {
        console.log(id)
        const response = await fetch(`/get-copy-injury-updates/${id}`);
        const data = await response.json();
        const textToCopy = data.text;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            alert('Text copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    } catch (error) {
        console.error('Error fetching text: ', error);
    }
}

const price_change=document.getElementById('copy_price_change')
if (price_change)
    price_change.addEventListener('click', CopyPriceChange);

for(let id=0;id<num_injuries;id++)
{
    const injury_updates=document.getElementById(`copy_injury_updates${id}`)
    if(injury_updates)
        injury_updates.addEventListener('click', () => CopyInjuryUpdates(id));
}