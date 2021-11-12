import Typography from '@mui/material/Typography';
import PrimaryAppBar from '../components/PrimaryAppBar';

function Home() {
    return (
      <div className="home">
        <PrimaryAppBar/>
        <Typography>
            HOMEPAGE!
        </Typography>
      </div>
    );
}

export default Home;