import banner from '../images/banner.png';
import '../css/Banner.css';

export const Banner = () => {
  return (
    <div className="d-flex justify-content-center align-items-center">
      <img src={banner} alt="My Image" className="img-fluid" style={{ maxHeight: '200px' }}/>
    </div>
  )
}