using System.Linq;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using UnityEngine;

public class CarAgent : Agent
{
    public float RotationAngle = 30;

    private Rigidbody rigidbody;
    private int[] Speed = new[] { 0, 15, 30 };
    private int[] RotAngle = new[] { 0, 15, 30 };

    private RayPerceptionSensorComponent3D raycastSensor;

    private Transform[] spawn_points;

    private LineRenderer sensor1Visual;
    private LineRenderer sensor2Visual;
    private LineRenderer sensor3Visual;

    private Transform sensor1;
    private Transform sensor2;
    private Transform sensor3;

    private Transform sensor1End;
    private Transform sensor2End;
    private Transform sensor3End;

    private float distance = 0;

    private bool collided = false;
    private float minimumDistanceToCollide = 1f;
    private int maximumDistance = 10;
    private float yAxisMinBound;
    private float yAxisMaxBound;

    // Start is called before the first frame update
    void Start()
    {
        rigidbody = GetComponent<Rigidbody>();
        spawn_points = GameObject.FindGameObjectsWithTag("spawn_point").Select(x => x.transform).ToArray();
        
        yAxisMaxBound = spawn_points[0].position.y + 10;
        yAxisMinBound = spawn_points[0].position.y - 10;

        sensor1 = GameObject.FindGameObjectWithTag("Sensor_1").transform;
        sensor2 = GameObject.FindGameObjectWithTag("Sensor_2").transform;
        sensor3 = GameObject.FindGameObjectWithTag("Sensor_3").transform;
        //Time.timeScale = 4;
    }

    void Update()
    {
        if (Input.GetKey("up") || Input.GetKey("down"))
        {
            rigidbody.velocity = transform.forward * Speed[1] * Input.GetAxis("Vertical");
        }
        if (Input.GetKey("left"))
        {
            transform.Rotate(0, -RotAngle[2] * Time.deltaTime, 0);
        }
        else if (Input.GetKey("right"))
        {
            transform.Rotate(0, RotAngle[2] * Time.deltaTime, 0);
        }
    }

    public override void OnEpisodeBegin()
    {
        var spawn_index = Random.Range(0, spawn_points.Length - 1);
        transform.position = spawn_points[spawn_index].position;
        transform.rotation = spawn_points[spawn_index].rotation;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        base.CollectObservations(sensor);
        RaycastHit ray;
        if(Physics.Raycast(sensor1.position, sensor1.forward, out ray, maximumDistance))
        {
            sensor.AddObservation(ray.distance);
        }
        else
        {
            sensor.AddObservation(maximumDistance);
        }

        if (Physics.Raycast(sensor2.position, sensor2.forward, out ray, maximumDistance))
        {
            sensor.AddObservation(ray.distance);
        }
        else
        {
            sensor.AddObservation(maximumDistance);
        }

        if (Physics.Raycast(sensor3.position, sensor3.forward, out ray, maximumDistance))
        {
            sensor.AddObservation(ray.distance);
        }
        else
        {
            sensor.AddObservation(maximumDistance);
        }
    }

    public override void OnActionReceived(float[] vectorAction)
    {
        var action = vectorAction[0];
        switch (action)
        {
            case 0:
                transform.Rotate(0, -RotAngle[2] * Time.deltaTime, 0);
                break;
            case 2:
                transform.Rotate(0, RotAngle[2] * Time.deltaTime, 0);
                break;
        }

        rigidbody.velocity = transform.forward * Speed[1];
        collided = MinRayHitDistance() < minimumDistanceToCollide;
        if (collided || transform.position.y > yAxisMaxBound || transform.position.y < yAxisMinBound)
        {
            SetReward(-1.0f);
            EndEpisode();
            collided = false;
        }
        else
        {
            SetReward(-0.05f);
        }
    }

    private float MinRayHitDistance()
    {
        RaycastHit ray;
        float hitDistance = maximumDistance;
        if (Physics.Raycast(sensor1.position, sensor1.forward, out ray, maximumDistance))
        {
            hitDistance = System.Math.Min(hitDistance, ray.distance);
        } 

        if (Physics.Raycast(sensor2.position, sensor2.forward, out ray, maximumDistance))
        {
            hitDistance = System.Math.Min(hitDistance, ray.distance);
        }

        if (Physics.Raycast(sensor3.position, sensor3.forward, out ray, maximumDistance))
        {
            hitDistance = System.Math.Min(hitDistance, ray.distance);
        }

        return hitDistance;
    }
}
