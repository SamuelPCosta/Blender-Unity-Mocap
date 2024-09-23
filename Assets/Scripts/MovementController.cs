using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.IO;

public class MovementController : MonoBehaviour
{
    [Header("Atributos da camera")]
    [Tooltip("distacia da camera para o usuário (em metros)")]
    [Range(0.1f, 5f)][SerializeField] private float distaciaDaCamera;
    public Transform cams;
    public Transform virtualCamera;
    public Transform ARCamera;

    [Header("Tare")]
    public GameObject headBone;
    public float headH = 1.7813f;

    [Header("Bones")]
    public GameObject[] bones;

    [Header("Starter")]
    public StartController _startController;

    //TARES
    private float xTarePosition = 0f;
    private float yTarePosition = 0f;
    private float zTarePosition = 0f;

    Dictionary<string, TransformData> transformDictionary = new Dictionary<string, TransformData>();

    public void Start()
    {
        cams.position = new Vector3(0, headH, -distaciaDaCamera);
        //float distancia = Mathf.Abs(virtualCamera.localPosition.z) - distaciaDaCamera;
    }

    private bool setVideo = false;

    void Update()
    {
        if (!setVideo && ARCamera.childCount > 0){
            Transform firstChild = ARCamera.GetChild(0);
            firstChild.gameObject.layer = LayerMask.NameToLayer("video");
            setVideo = true;
        }

        if(_startController.isConverting)
            convertMovement();
        else
            setFalse();

        //Debug.Log("{json}");
    }

    public void setFalse()
    {
        string json = JsonUtility.ToJson(new TransformListWrapper { start = false, bones = null }, true);
        string path = Path.Combine(Application.persistentDataPath, "transformData.json");
        File.WriteAllText(path, json);
    }

    void OnDisable()
    {
        setFalse();
    }

    public void setTare()
    {
        if (zTarePosition == 0f) {
            xTarePosition = headBone.transform.position.x;
            yTarePosition = headBone.transform.position.y;
            zTarePosition = headBone.transform.position.z;

            //if(headBone.transform.position.y > headH)
            //    yTarePosition = yTarePosition * -1;

            //ajusta sentido
            xTarePosition *= -1;
            yTarePosition *= -1;
            zTarePosition *= -1;
        }
    }

    private void convertMovement()
    {
        List<TransformData> transformList = new List<TransformData>();

        for (int i = 0; i < bones.Length; i++)
        {
            TransformData transformData = packValues(i);
            transformData.name = bones[i].name;  // Atribui o nome do objeto
            transformList.Add(transformData);
        }

        string json = JsonUtility.ToJson(new TransformListWrapper { start = _startController.isConverting, bones = transformList }, true);
        string path = Path.Combine(Application.persistentDataPath, "transformData.json");
        File.WriteAllText(path, json);
    }

    private TransformData packValues(int i){
        Quaternion localRotation = bones[i].transform.localRotation;
        Quaternion rotation = Quaternion.Euler(90f, 0f, 0f);
        Quaternion rotatedQuaternion = localRotation * rotation;
        RotationData rotationData = new RotationData
        {
            x = (float)Math.Round(rotatedQuaternion.x * -1, 2),
            y = (float)Math.Round(rotatedQuaternion.y * -1, 2),
            z = (float)Math.Round(rotatedQuaternion.z, 2),
            w = (float)Math.Round(rotatedQuaternion.w, 2)
        };

        Vector3 localPosition = bones[i].transform.localPosition;
        LocationData locationData = new LocationData
        {
            x = (float)Math.Round((localPosition.x + xTarePosition), 2),
            y = (float)Math.Round((localPosition.y + yTarePosition), 2),
            z = (float)Math.Round(((localPosition.z + zTarePosition) * - 1), 2)
        };

        TransformData transformData = new TransformData
        {
            Location = locationData,
            Rotation = rotationData
        };

        //Debug.Log(json);
        //string json = JsonUtility.ToJson(transformData, true);
        return transformData;
    }

    [System.Serializable]
    public class TransformListWrapper
    {
        public bool start;
        public List<TransformData> bones;
    }
}
