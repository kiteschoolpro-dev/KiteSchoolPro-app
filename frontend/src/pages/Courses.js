import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { courseApi } from '../services/api';
import { Wind, Clock, Users, MapPin, Euro, ArrowRight } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const courseTypeLabels = {
  private_kitesurf: 'Private Kitesurfing',
  semi_private_kitesurf: 'Semi-Private Kitesurfing', 
  efoil_coaching: 'E-Foil Coaching',
  efoil_test: 'E-Foil Test Session'
};

const spotLabels = {
  sylt: 'Sylt',
  romo: 'Rømø'
};

export default function Courses() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSpot, setSelectedSpot] = useState('all');
  const [selectedType, setSelectedType] = useState('all');

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const data = await courseApi.getAll();
      setCourses(data);
    } catch (error) {
      console.error('Failed to load courses:', error);
      setError('Failed to load courses. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filteredCourses = courses.filter(course => {
    if (selectedSpot !== 'all' && !course.spots.includes(selectedSpot)) {
      return false;
    }
    if (selectedType !== 'all' && course.course_type !== selectedType) {
      return false;
    }
    return true;
  });

  const CourseCard = ({ course }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {course.name}
            </h3>
            <p className="text-gray-600 text-sm mb-4 line-clamp-2">
              {course.description}
            </p>

            <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
              <div className="flex items-center text-gray-500">
                <Clock className="h-4 w-4 mr-2" />
                {course.duration_hours}h session
              </div>
              <div className="flex items-center text-gray-500">
                <Users className="h-4 w-4 mr-2" />
                Max {course.max_students} student{course.max_students > 1 ? 's' : ''}
              </div>
              <div className="flex items-center text-gray-500">
                <MapPin className="h-4 w-4 mr-2" />
                {course.spots.map(spot => spotLabels[spot]).join(', ')}
              </div>
              <div className="flex items-center text-gray-500">
                <Wind className="h-4 w-4 mr-2" />
                {course.skill_level_required}
              </div>
            </div>

            {course.equipment_included.length > 0 && (
              <div className="mb-4">
                <p className="text-xs font-medium text-gray-500 mb-1">Equipment Included:</p>
                <div className="flex flex-wrap gap-1">
                  {course.equipment_included.slice(0, 3).map((item, index) => (
                    <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                      {item.replace('_', ' ')}
                    </span>
                  ))}
                  {course.equipment_included.length > 3 && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-600">
                      +{course.equipment_included.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center">
            <Euro className="h-5 w-5 text-green-600 mr-1" />
            <span className="text-2xl font-bold text-gray-900">
              {course.base_price}
            </span>
            <span className="text-gray-500 ml-1">per person</span>
          </div>
          
          <Link
            to={`/courses/${course.id}/book`}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
          >
            Book Now
            <ArrowRight className="h-4 w-4 ml-2" />
          </Link>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">
          Watersports Courses
        </h1>
        <p className="mt-2 text-gray-600 max-w-2xl mx-auto">
          Choose from our range of professional kitesurfing and e-foil courses at Sylt and Rømø. 
          All equipment included with certified instructors.
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Location
            </label>
            <select
              value={selectedSpot}
              onChange={(e) => setSelectedSpot(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="all">All Locations</option>
              <option value="sylt">Sylt</option>
              <option value="romo">Rømø</option>
            </select>
          </div>

          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Course Type
            </label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="all">All Courses</option>
              <option value="private_kitesurf">Private Kitesurfing</option>
              <option value="semi_private_kitesurf">Semi-Private Kitesurfing</option>
              <option value="efoil_coaching">E-Foil Coaching</option>
              <option value="efoil_test">E-Foil Test</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {/* Courses Grid */}
      {filteredCourses.length === 0 ? (
        <div className="text-center py-12">
          <Wind className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No courses found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your filters to see more courses.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}
    </div>
  );
}