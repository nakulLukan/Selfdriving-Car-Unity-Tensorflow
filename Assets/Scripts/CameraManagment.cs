using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraManagment : MonoBehaviour
{
    private Transform Player;
    private Vector3 cameraInitPosition;
    // Start is called before the first frame update
    void Start()
    {
        Player = GameObject.FindGameObjectWithTag("Player").transform;
        cameraInitPosition = Player.position - transform.position;
    }

    // Update is called once per frame
    void Update()
    {
        transform.position = Player.position - cameraInitPosition;
        transform.LookAt(Player);
    }
}
